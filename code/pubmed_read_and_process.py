

import xml.etree.ElementTree as ET 
import pandas as pd
import re
import dns.resolver
  

def format_data():
    # create element tree object 
    tree = ET.parse("pubmed_results.xml") 

    # get root element 
    root = tree.getroot() 
    data={}
    for article in root.findall('.//PubmedArticle'): 
        #print(article.find(".//PMID").text)
        pmid = article.find(".//PMID").text
        authors = article.findall(".//AuthorList//Author")
        if authors is None:
            continue
        
        for author in authors:
            if author.find(".//ForeName") is None or author.find(".//LastName") is None:
                continue

            name = author.find(".//ForeName").text
            last_name = author.find(".//LastName").text

            affiliation_info = author.findall(".//AffiliationInfo//Affiliation")
            author_affs = set() #set
            for affiliation in affiliation_info:
                author_aff = affiliation.text
                author_affs.add(author_aff)

            if f"{name} {last_name}" not in data:

                data[f"{name} {last_name}"] = {"name": name, "last_name": last_name, "affiliations": author_affs, "pmid": {pmid}}

            else:
                data[f"{name} {last_name}"]["pmid"].add(pmid)
                data[f"{name} {last_name}"]["affiliations"].update(author_affs)

    df = pd.DataFrame.from_dict(data=data.values(), orient='columns')
    df['total_articles'] = df.pmid.apply(lambda x: len(x))
    
    '''extracting emails'''
    df = df.explode(column = "affiliations").explode(column='pmid') #expanding rows by affiliations
    df.affiliations.astype(str)
    df['emails'] = df.affiliations.str.extract(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+)') #extract emails
    df = df.groupby(['name', 'last_name','total_articles']).agg({'affiliations': lambda x: set(x.tolist()), 'pmid': lambda x: x.tolist(), 'emails': lambda x: x.tolist()}).reset_index()
    df['emails'] = df['emails'].apply(lambda x: {i for i in x if not pd.isna(i)}) #going back unique rows per author and deleting NaNs in list of emails
    df.to_csv("task2_question1.csv")
    return df

def score_people(df):

    df.sort_values(by='total_articles', inplace = True, ascending = False)
    df.head(5).to_csv("task_2_question_2.csv")

    return df


'''
Implement a check for the quality of the extracted email addresses.
Come up with a definition of what is a “good” email address for our product and customers. Label the emails that you propose to include into the product.
'''



# List of common disposable email domains
DISPOSABLE_DOMAINS = [
    "mailinator.com", "trashmail.com", "10minutemail.com", "tempmail.com"
]

# List of blacklisted domains
BLACKLISTED_DOMAINS = [
    "spamdomain.com", "163.com"
]

# Function to check if domain has MX records
def has_mx_record(domain) -> bool:
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return len(mx_records) > 0
    except:
        return False

# Function to check if email is from disposable or blacklisted domain
def is_disposable_or_blacklisted(email)-> bool:
    domain = email.split('@')[-1]
    return domain in DISPOSABLE_DOMAINS or domain in BLACKLISTED_DOMAINS


def score_email(row) -> int:
    score = 0
    email = str(row['emails']).lower()
    last_name = str(row['last_name']).lower()
    name = str(row['name']).lower()
    domain = email.split('@')[-1]

    if is_disposable_or_blacklisted(email):
        return -1 #enails to be discarded
    
    if 'edu' in domain:#well known domains, e.g from companies or .edu meaning from universities
        score +=1
        
    if has_mx_record(email):
        score += 1
    
    if last_name in email:
        score += 1

    if name in email:
        score += 1
    
    return score

def label_email(row) -> str:
    score = row['email_score']

    if score <= 0:
        return "bad"
    
    else:
        return "good"

def score_and_label(df):

    df['email_score'] = df.apply(score_email, axis=1)
    df["label"] = df.apply(label_email, axis=1)
    df = df[["emails", "email_score","label","name","last_name"]]
    df.to_csv("task2_question_5.csv")
    
    return df


if __name__ == "__main__":

    print("starting")
    df = format_data()
    print(df.head(10))
    df_2 = score_people(df)
    print(df_2.head(10))
    df_email = df.explode(column = 'emails')
    df_email = score_and_label(df_email)
    print(df_email[["emails", "email_score","label","name","last_name"]])
    print("end")

   