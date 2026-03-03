#!/usr/bin/env python3
"""
Take a presentation linkbase url link and pull the oancf tag that identifies the line item as presented on the Statement of Cash Flows

Usage:
  python pull_oancf.py <email_address> https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_pre.xml
"""

import argparse
import sys
import requests
from requests.exceptions import HTTPError
from lxml import etree

LINKBASE_NS = "http://www.xbrl.org/2003/linkbase"
XLINK_NS = "http://www.w3.org/1999/xlink"

NS = {
    "link": LINKBASE_NS,
    "xlink": XLINK_NS
}

def fetch_response(user, url):

    headers = {"User-Agent": user,
          "Accept-Encoding": "gzip, deflate",
          "Host": "www.sec.gov"
          }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')

def format_tree(response):
    tree = etree.fromstring(response.content)

    return tree

def isolate_cashflow_presentationLink(tree):

    matching_roles = []

    presentation_links = tree.xpath("//link:presentationLink", namespaces=NS)

    for pl in presentation_links:
        role = pl.get(f"{{{XLINK_NS}}}role") or ""

        if "cashflow" not in role.lower():
            continue

        locs = pl.xpath(".//link:loc", namespaces=NS)

        labels = [(loc.get(f"{{{XLINK_NS}}}label") or "").lower() for loc in locs]

        has_operating = any("operating" in lbl for lbl in labels)
        has_investing = any("investing" in lbl for lbl in labels)
        has_financing = any("financing" in lbl for lbl in labels)

        if has_operating and has_investing and has_financing:
            matching_roles.append(role)

    if len(matching_roles) == 1:
        return(matching_roles[0])
    elif len(matching_roles) == 0:
        print("No presentationLink with Cash Flow role")
    else:
        print("Multiple presentationLinks matching Cash Flow role")

def identify_root_locator(tree, presentationLink_role):
    """
    Given XML tree and a presentationLink xlink:role string,
    return loc labels that appear in xlink:from but not in xlink:to.
    """

    pl = tree.xpath(
        "//link:presentationLink[@xlink:role=$r]",
        namespaces=NS,
        r=presentationLink_role
    )

    #TO-DO: add in functionality to have exception cases where there is more than one presentationLink matching the role

    from_labels = set(pl[0].xpath(".//link:presentationArc/@xlink:from", namespaces=NS))
    to_labels   = set(pl[0].xpath(".//link:presentationArc/@xlink:to", namespaces=NS))

    list_of_labels = sorted(from_labels - to_labels)

    if len(list_of_labels) == 1:
        return list_of_labels[0]
    elif len(list_of_labels) == 0:
        print("No root")
    else:
        print("Multiple roots")

def find_operating_to(tree, from_label):
    """
    Given an xlink:from label, return xlink:to labels
    that contain 'operating' (case-insensitive).
    """

    # Find all arcs with matching xlink:from
    arcs = tree.xpath(
        "//link:presentationArc[@xlink:from=$f]",
        namespaces=NS,
        f=from_label
    )

    operating_targets = []

    for arc in arcs:
        to_label = arc.get(f"{{{XLINK_NS}}}to")
        if to_label and "operating" in to_label.lower():
            operating_targets.append(to_label)

    return operating_targets[0]

def max_order_child(tree, operating_target):
    """
    Given an xlink:from label (operating_target),
    return the xlink:to label with the maximum order value.
    """
    arcs = tree.xpath(
        "//link:presentationArc[@xlink:from=$f]",
        namespaces=NS,
        f=operating_target
    )

    if not arcs:
        return None

    # Select arc with maximum numeric order
    max_arc = max(
        arcs,
        key=lambda arc: float(arc.get("order", "0"))
    )

    return max_arc.get(f"{{{XLINK_NS}}}to")

def get_href_by_label(tree, label):
    """
    Return the xlink:href of the <link:loc> whose xlink:label matches `label`.
    """
    locs = tree.xpath(
        "//link:loc[@xlink:label=$lbl]",
        namespaces=NS,
        lbl=label
    )

    if not locs:
        return None

    return locs[0].get(f"{{{XLINK_NS}}}href").split("#")[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, help="email for EDGAR User-Agent header declaration (you will not be emailed)")
    parser.add_argument("--url", type=str, help="URL of presentation linkbase from EDGAR")
    args = parser.parse_args()

    if not args.user:
        args.user = input("Please enter email for EDGAR User-Agent header declaration (you will not be emailed): ")
    
    if not args.url:
        args.url = input("Please enter URL of presentation linkbase from EDGAR: ")
    
    if not args.user or not args.url:
        raise ValueError("Both email and URL must be provided.")

    url_response = fetch_response(args.user, args.url)
    formatted_tree = format_tree(url_response)
    cashflow_presentationLink = isolate_cashflow_presentationLink(formatted_tree)
    root_node = identify_root_locator(formatted_tree, cashflow_presentationLink)
    xlink_to = find_operating_to(formatted_tree, root_node)
    label = max_order_child(formatted_tree, xlink_to)
    oancf_tag = get_href_by_label(formatted_tree, label)

    print(f"**The XBRL tag corresponding to the Operating Cash Flow line item as-filed is: {oancf_tag}")
    return(oancf_tag)


if __name__ == "__main__":
    main()
