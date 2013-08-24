import re
import requests
from bs4 import BeautifulSoup

SCOPUS_QUERY = "http://www.scopus.com/inward/record.url?partnerID=HzOxMe3b&scp={0}"

SCOPUS_AUTHOR_CITATIONS_QUERY = "http://www.scopus.com/results/results.url?cc=10&sort=plf-f&src=s&nlo=&nlr=&nls=&citedAuthorId={0}&imp=t&sid=B258E6F5B48D0BD0B55047E882ADEF0B.WlW7NKKC52nnQNxjqAQrlA%3a500&sot=cite&sdt=cite&sl=0&ss=plf-f&ws=r-f&ps=r-f&cs=r-f&origin=resultslist&zone=resultslist"

DELIM = ","

YULY_AUTHOR_ID = 13609110700
id_list = [69349095671, 9244254745]


# Get a list of IDs
def papers_for_author(auth_id):
	paper_ids = []

	res = requests.get(SCOPUS_AUTHOR_CITATIONS_QUERY.format(auth_id))
	soup = BeautifulSoup(res.content)

	for paper_href in soup.find_all("a", {"href":re.compile(r"^http://www.scopus.com/record/")}):
		# assume one ID per section
		# TODO: can apply re.findall on the entire result instead of souping it 
		new_id = re.findall("display\.url\?eid=2-s2\.0-(\d*?)\&", paper_href.encode())[0]
		paper_ids.append(new_id)
	
	return paper_ids



def metadata_for_papers(paper_ids, outfile):
	fout = open(outfile,"w") 

	fout.write("paper_id{0}pubmed_id{0}author_ids\n".format(DELIM))

	for i, paper_id in enumerate(paper_ids):
		# Counter
		if i % 5 == 0:
			print i

		# Execute query, convert result to Soup format
		#try:
		res = requests.get(SCOPUS_QUERY.format(paper_id))
		soup = BeautifulSoup(res.content)
		
		# get author list
		authors_section = soup.find(id="authorlist").encode_contents()
		author_list = re.findall(r"\?authorId=(.*?)\&", authors_section)
		authors_str = DELIM.join(author_list)

		# get pubmed ID
		try:
			# assume there's only one
			pubmed_id = re.findall(r"\"View in PubMed\">(.*?)<", soup.encode_contents())[0]
		except IndexError:
			# no pubmed ID
			print i, ":no pubmed ID"
			pubmed_id = ""

		# write to file
		fout.write("{1}{0}{2}{0}{3}\n".format(DELIM, paper_id, pubmed_id, authors_str ))
		#except:
		#	# Can't find ID or something went wrong
		#	fout.write("{0}\n".format(paper_id))

	fout.close()

	#print res.text()

if __name__ == "__main__":

	# get a list of paper ID by finding the papers citing a given author
	id_of_citing_papers = papers_for_author(YULY_AUTHOR_ID)
	print id_of_citing_papers

	# write their metadata to a file
	metadata_for_papers(id_of_citing_papers, "sample.csv")
