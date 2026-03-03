Best Practices on leveraging XBRL files to obtain financial information

First, we must identify the correct tag that the Company uses to obtain our line item of interest. To do so, we will leverage the presentation linkbase.

Procedure:

1. Search through "link:presentationLink" elements that contain "CashFlow" in the "xlink:role"
2. To verify we have identified the right "presentationLink" element, check if there is a "loc" element within the "presentationLink" that contains the word "Operating", "Investing", and "Financing"
3. Find the root "loc" element by searching through for the "loc" that exists in "xlink:from" but not "xlink:to"
4. Once you find the root "loc" element, pull all "loc" elements that are "xlink:to" the root "loc".
5. Of these "loc" elements, find the element relating to "Operating Activities"
6. Find all "presentationArc" elements that contain the "xlink:from" as the "loc" identified in step 7, and identify the "presentationArc" with the highest "order" attribute.
7. From the identified "presentationArc" from step 8, select the "xlink:to" attribute. This identifies the "loc" element which will be the final value presented in the operating activities section of the cash flow statement.
8. To pull the corresponding XBRL tag, access the "loc" element identified in step 9, and pull the tag from the "xlink:href" element after the "#" delimiter 
