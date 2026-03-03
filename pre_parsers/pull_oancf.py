#!/usr/bin/env python3
"""
Take a presentation linkbase url link and pull the oancf value as presented on the Statement of Cash Flows

Usage:
  python pull_oancf.py https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_pre.xml
"""

import requests
from requests.exceptions import HTTPError
from lxml import etree

LINKBASE_NS = "http://www.xbrl.org/2003/linkbase"
XLINK_NS = "http://www.w3.org/1999/xlink"

NS = {
    "link": LINKBASE_NS,
    "xlink": XLINK_NS
}

def fetch_response(url):

    headers = {"User-Agent": "patrick.chen3@marshall.usc.edu",
          "Accept-Encoding": "gzip, deflate",
          "Host": "www.sec.gov"
          }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}') # Includes details of the failed request
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
        to_label = arc.get("{http://www.w3.org/1999/xlink}to")
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

    return max_arc.get("{http://www.w3.org/1999/xlink}to")

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

    return locs[0].get("{http://www.w3.org/1999/xlink}href").split("#")[-1]


url = "https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_pre.xml"
response = fetch_response(url)
tree = format_tree(response)
role = isolate_cashflow_presentationLink(tree)
root = identify_root_locator(tree, role)
xlink_to = find_operating_to(tree, root)
label = max_order_child(tree, xlink_to)

oancf_tag = get_href_by_label(tree, label)
print(oancf_tag)