### Best practices on leveraging XBRL files to obtain financial information

First, we must identify the correct tag that the Company uses to obtain our line item of interest. To do so, we will leverage the presentation linkbase.

#### Procedure for oancf:

1. Search through "link:presentationLink" elements that contain "cashflow" in the "xlink:role"
2. To verify we have identified the right "presentationLink" element, check if there are "loc" elements within the "presentationLink" that contain the words "Operating", "Investing", and "Financing"
3. Find the root "loc" element by searching through for the "loc" that exists in "xlink:from" but not "xlink:to"
4. Once you find the root "loc" element, identify the "loc" elements linked to the root with the "xlink:to" attribute.
5. Of these "loc" elements linked to the root, find the element containing the word "operating" for Operating Activities.
6. Find all "presentationArc" elements that contain the "xlink:from" as the "loc" identified in step 5, and identify the "presentationArc" with the highest "order" attribute.
7. From the identified "presentationArc" from step 6, return the "xlink:to" attribute. This identifies the "loc" element which will be the final value presented in the operating activities section of the cash flow statement.
8. To pull the corresponding XBRL tag, access the "loc" element identified in step 7, and pull the tag from the "xlink:href" element after the "#" delimiter.

To run the code:

```bash
python pull_oancf.py --user <email_address> --url <url>

#or

#interative terminal prompts will request inputs for email address and URL.
python pull_oancf.py
```

Example output at url [https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_pre.xml](https://www.sec.gov/Archives/edgar/data/320193/000032019325000079/aapl-20250927_pre.xml):
`**The XBRL tag corresponding to the Operating Cash Flow line item as-filed is: us-gaap_NetCashProvidedByUsedInOperatingActivities`