# News Checker

This is a streamlit application that dynamically scrapes news articles for a given date and checks for plagiarism between five of the most popular news websites in Ghana. This web application is hoste on Amazon EC2 and can be [accessed here](http://98.82.9.62:8501/)

#### PROBLEM STATEMENT
Although journalism in Ghana has come a long way in Ghana, many Ghanaians believe the quality of journalism in Ghana has taken a nosedive, especially in the era of social media, where viral content is priced over quality news articles. As such, it is very common to see many news organizations copying and publishing news articles without verifying the source or content. This had made it difficult for many people to completely trust articles published by most news organizations, including some of the most respected organizations such as 3News and Joy News. That is why I built this algorithm and web application to determine the proportion of published articles plagiarized by a news organization within a given period. 

#### AIM AND OBJECTIVES
* Determine the proportion of published articles plagiarized by a news organization within a given period.
* Determine the plagiarized articles and their percentage of similarities.
* Present a visual analysis of the data in graphs.

#### METHODOLOGY
* #### WEB SCRAPING
  This project starts with building a web scraping tools for 5 of the most popular news websites in Ghana namely: Ghanaweb, 3News, MyJoyOnline, Yen Ghana, and Modern Ghana. This scraping tool is also very dynamic, which allows users to decide which news article categories and what time frame they'd want to compare articles.
* #### PLAGIARISM CHECKER
  To build the plagiarism tool, the articles are collected into a pandas data frame. Each article is then cleaned to remove any non-alphabetic characters. The article text is then broken down into words. Any word with len <2 is removed from the list (eg. a, I), as well as if it is equal to any of the widely used stopwords (eg “the,” “an,” or “in”). The words are then lematized, that is, words such as "running" or "cats" are reduced to their basic form in "run" and "cat" respectively.  After that, the words are pieced together as a text, and vectorized using TfidfVectorizer. Cosine_similarity, which is a package from scikit_learn was then used to calculate the the level of similarity between vectors. The resultant data is then analyzed an mapped back to the dataset to identify the plagiarized articles and the organizations that published the said articles.
#### STREAMLIT WEB APPLICATION
* After all this, a streamlit application was built to allow others the ability to use this tool.

#### SIGNIFICANCE
* This could give policymakers a tool to easily access and understand the current situation in the quality of Ghanaian journalism.
* This could also provide news organizations the ability to easily determine which articles are being copied by which organization without attribution. They could use this tool to assess the proportion their articles which have been plagiarised within any given timeframe.




