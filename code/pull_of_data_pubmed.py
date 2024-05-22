from Bio import Entrez

# Always set your email address
Entrez.email = "mililic85@gmail.com"

# Step 1: Search for articles
search_term = "Wegovy"
handle = Entrez.esearch(db="pubmed", term=search_term, sort = "pub_date", datetype = "pdat", mindate = "2022/01", maxdate = "2024", retmax=2000)
search_results = Entrez.read(handle)
handle.close()

# Step 2: Fetch the data in "PubMed" format
pmids = search_results["IdList"]
print(len(pmids))
handle = Entrez.efetch(db="pubmed", id=pmids, rettype="pubmed", retmode="text")
pubmed_data = handle.read()
handle.close()

# Step 3: Save the data to a file
with open("pubmed_results.xml", "w") as file:
    file.write(pubmed_data)

# Step 4: Parse the "PubMed" format results
# Here we print the results directly; parsing can be done as needed.

#print(pubmed_data)


