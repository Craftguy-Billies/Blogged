import trafilatura
import requests
from bs4 import BeautifulSoup
import ast
import json
import time
import random
import os
from groq import Groq

DEBUG = False
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
client = Groq()

def crawl_top_10_results(query, nor=10):
    encoded_query = requests.utils.quote(query)
    url = f"https://www.google.com/search?q={encoded_query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='tF2Cxc')[:nor]:
        result = {}
        if g.find('h3'):
            result['title'] = g.find('h3').text
        if g.find('a'):
            result['url'] = g.find('a')['href']
        snippet = ''
        if g.find('span', class_='aCOpRe'):
            snippet = g.find('span', class_='aCOpRe').text
        elif g.find('div', class_='IsZvec'):
            snippet = g.find('div', class_='IsZvec').text
        elif g.find('div', class_='VwiC3b'):
            snippet = g.find('div', class_='VwiC3b').text
        elif g.find('div', class_='s3v9rd'):
            snippet = g.find('div', class_='s3v9rd').text
        result['snippet'] = snippet
        results.append(result)

    return results

def extract_list_content(input_string):
    start_index = input_string.find("[")
    end_index = input_string.rfind("]")

    if start_index != -1 and end_index != -1 and start_index < end_index:
        try:
            return ast.literal_eval(input_string[start_index:end_index + 1])
        except (ValueError, SyntaxError):
            return []
    else:
        return []

def extract_json_content(input_string):
    start_index = input_string.find("{")
    end_index = input_string.rfind("}")

    if start_index != -1 and end_index != -1 and start_index < end_index:
        try:
            return ast.literal_eval(input_string[start_index:end_index + 1])
        except (ValueError, SyntaxError):
            return {}
    else:
        return {}

def titler(outline, query, model, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            full_article = ""
            prompt = f"""
            i want to write a blog article of the keyword {query}.
            here is all the <h2> headers i am going to cover in my blog article:
            {outline}

            i want a title that is clickbait enough, can convey the information I want to discuss about, in moderate length and humanized tone.
            it must be informational intent. words like "盤點", "攻略", "方法" are favored.
            if you add numbers like '7大', make sure it matches the content of headers. (some headers may cover more than one information)
            you should SEO optimize the title with the keyword {query} naturally.
            return me a single JSON object with single key 'title' without premable and explanations.
            AGAIN: NO premable and explanation needed.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            article_title = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    article_title += chunk.choices[0].delta.content

            article_title = extract_json_content(article_title)["title"]
            if article_title:
                  return article_title

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def structurer(result_list, query, model, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            full_article = ""
            prompt = f"""
            i want to write a blog article of the keyword {query}.
            here is the top 10 results when i search for this keyword:
            {result_list}

            i want to take some articles as reference. i only want informational intent results, and addressing my topic.
            you should return 5-9 results after filtering.
            return me a list of useful search results in the same format: each list item is a JSON object with title, url and snippet.
            no premable and explanation needed.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            filtered_headers = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    filtered_headers += chunk.choices[0].delta.content

            filtered_headers = extract_list_content(filtered_headers)
            if filtered_headers:
                  return filtered_headers

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def topic_definer(website_text, query, model, lang, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            prompt = f"""
            i want to write a blog article of the keyword {query}.
            here is the website text for a top ranked article writing about the topic:
            {website_text}

            identify the topics that they wrote, and reform them into h2 headers.
            output in {lang}
            return me a python list of h2 headers.
            NO premable and explanation. I only want the list without other words.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            filtered_headers = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    filtered_headers += chunk.choices[0].delta.content

            filtered_headers = extract_list_content(filtered_headers)
            if filtered_headers:
                    return filtered_headers

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def topic_refiner(topics, query, model, lang, size, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            prompt = f"""
            for this keyword: {query}
            here is the headers that top ranked articles write about, without ordering:
            {topics}

            now i want to write a blog article about this topic. expected blog size: large
            from the topics of top ranked articles, PICK best h2 headers with consistent level of specificity, and rewrite me these h2 headers.
            EVERY HEADER SHOULD BE DISTINCT ASPECT! NO DUPLICATION!
            do not give duplicated headers. headers must be DISTINCT and cannot have DUPLICATED ASPECTS. do not give totally unrelated headers.
            the h2 headers given should be distinct, non-repetitive, and focused. no generic or catch-all phrases. specific is MUST. no need elaboration in headers if not mentioned in original header. DO NOT form headers by clustering other's multiple headers. i need PICK and REWRITE.
            my inner content will be slightly different from reference article, so make sure headers are reformed.
            quality should be prioritized, less headers are better than vague and overly broad headers. no generic or catch-all phrases.
            headers should be in {lang}
            return me a python list of headers only.
            NO premable and explanation needed.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            filtered_headers = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    filtered_headers += chunk.choices[0].delta.content

            filtered_headers = extract_list_content(filtered_headers)
            filtered_headers = topic_selector(filtered_headers, query, model, lang, size)
            if filtered_headers:
                    return filtered_headers

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def topic_selector(headers, query, model, lang, size, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            prompt = f"""
            i want to write a blog article of the keyword {query}.
            now here is the proposed h2 headers for writing:
            {headers}
            but there might be duplicated aspects, or headers with unclear intent.
            there might be vague headers with different level of specificity as well.
            for example, '深圳必訪景點' and '深圳龍華區甜品店' is having significantly different level of specificity. in this case, remove the bigger coverage one, i.e. '深圳必訪景點'
            delete these vague or inappropriate headers ONLY. no need to modify acceptable headers.
            expected header count: {size}, filter the best headers i needed only.
            EVERY HEADER SHOULD BE DISTINCT ASPECT!
            output in {lang}
            return me a python list of h2 headers.
            NO premable and explanation. I only want the list without other words.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            filtered_headers = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    filtered_headers += chunk.choices[0].delta.content

            filtered_headers = extract_list_content(filtered_headers)
            if filtered_headers:
                  return filtered_headers

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def headerizer(result_list, query, model, lang, size):
    url_list = []
    for result in result_list:
        url_list.append(result["url"])

    all_topics = []

    for url in url_list:
        downloaded = trafilatura.fetch_url(url)
        website_text = trafilatura.extract(downloaded)
        if website_text:
            topics = topic_definer(website_text, query, model, lang)
            all_topics.extend(topics)

    all_topics = topic_refiner(all_topics, query, model, lang, size)
    return all_topics

def querier(header, query, model, lang, max_retries=3, delay=2):
    attempt = 0
    while attempt < max_retries:
        try:
            prompt = f"""
            i am writing article with this keyword: {query}
            i need to do information research before writing
            for this specific header in the article {header}, i want you to craft me a web search query that can obtain most accurate information results to write the paragraphs under this header.
            You MUST ensure the search query is accurate information, to prevent search results points to other services or keywords.
            craft the search query in {lang}
            return me a python list object with each list item a JSON object with a single key query without any premable and explanations. you can return more than one JSON object search query in the list.
            NO premable and explanation. Dont give me more than one list.
            """

            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt.strip()}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=8000,
                stream=True
            )

            thequery = ""
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    thequery += chunk.choices[0].delta.content

            thequery = extract_list_content(thequery)
            if thequery:
                  return thequery

        except Exception as e:
            attempt += 1
            if attempt < max_retries:
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(sleep_time)
            else:
                raise

def pf_rewriter(article, header, lang, title, model):
    full_article = ""
    prompt = f"""
    title of the crawled article:
    {title}

    content of article:
    {article}

    i want to write paragraphs under the header {header}
    first, by seeing the title and content of article, understand the header is a noun or just a general concept. DO NOT misunderstand a general genre as a specific noun, as everything written will be wrong afterwards.
    generate me point forms for related information ONLY. do not give me related aspects.
    if the information i provided is referring to another service or information instead of the information looking for, return no results is better than wrong information.
    make sure you do not misidentify details. this is a MUST. make sure you did a summary check and ensure the bullet points are 100% correct without misidentifying events or information subject.
    you must label general information if the information is not directly addressing this specific header. (be careful of wrong country, district, human names, if they match the header)
    return me in {lang}. no premable and explanation.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8000,
        stream=True
    )

    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            full_article += chunk.choices[0].delta.content

    return full_article

def ai_rewriter(bullet_points, header, lang, model):
    full_article = ""
    prompt = f"""
    {bullet_points}
    you are a helpful writing assistant, expertize in writing fluently and in a blogging tone.
    i want to write paragraphs under the h2 header {header}
    by seeing the bullet points, make sure you understand the header is a noun or just a general concept. DO NOT misunderstand a general genre as a specific noun, as everything written will be wrong afterwards.
    DO NOT GIVE INCONSISTANT INFORMATIONS! Comprehend the content and give me a consistent answer if there are two version of answers.
    you must only give me ONE <h2> in this reply.
    generate me paragraphs. be detailed. you can elaborate to generate longer paragraphs, but make sure your elaboration is not by guessing or exaggerating.
    do not include promotions, and make sure the tone of rewriting is professional. make sure your returned paragraphs are coherent and fluent, instead of point form like paragraphs.
    your rewriting need to be humanized and fluent. prioritize fluency over informative.
    your replies must base on the web search information. do not create information.
    return me in a HTML form. text must be labelled with html tags.
    you can add <h3> if needed. but do not overuse.
    return me in {lang}. no premable and explanation.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8000,
        stream=True
    )

    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            full_article += chunk.choices[0].delta.content

    return full_article

def combine_multiline_strings(*strings):
    return "\n".join(strings)

def get_title_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        return title
    except requests.exceptions.RequestException as e:
        return None
    except Exception as e:
        return None

def metadataer(outline, query, lang, model):
    prompt = f"""
    i am writing article with this keyword: {query}
    now i need two HTML tags, <meta name="description" content=""> and <meta name="keywords" content="">
    i need you to help me fill in the content part, using NLP techniques, SEO optimized naturally with the below main keyword and headers:
    main keyword: {query}
    all h2 headers: {outline}
    i only want you to return me the two HTML meta tags, properly formatted as HTML structure, and return me without premable and explanations.
    output the description content and keywords content in {lang}.
    AGAIN: NO premable and explanations.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8000,
        stream=True
    )

    metadata = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            metadata += chunk.choices[0].delta.content

    return metadata

def introer(outline, title, lang, model, max_retries=3, delay=2):
    prompt = f"""
    i want to write a blog article with title: {title}
    the headers i have written is as below:
    {outline}
    i want you to craft me an introductory paragraph that can captivate readers to continue reading. It can be a bit clickbait style.
    starting with a question is preferred.
    return me the introductory paragraph with <p> tags around.
    return me in {lang}. no premable and explanation.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8000,
        stream=True
    )

    full_article = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            full_article += chunk.choices[0].delta.content

    return full_article

def outline_editing(outline):
    print("Generated Outline:")
    print(outline)

    user_input = input("Do you want to modify the outline? (y/n): ").strip().lower()

    if user_input == 'y':
        while True:
            try:
                print("Please input the modified outline as a Python list (e.g., ['Header1', 'Header2', 'Header3']):")
                modified_outline = eval(input("Modified outline: ").strip())

                if isinstance(modified_outline, list):
                    return modified_outline
                else:
                    print("Invalid format! Outline should be a list. Please try again.")

            except Exception as e:
                print(f"Error: {e}. Please input a valid Python list format.")
    else:
        return outline

def autoblogger(query, model, size, lang, outline_editor):
    outline = headerizer(structurer(crawl_top_10_results(query), query, model), query, model, lang, size)
    if outline_editor:
      outline = outline_editing(outline)
    final_article = ""
    title = titler(outline, query, model)
    metadata = metadataer(outline, query, lang, model)
    intro = introer(outline, title, lang, model)
    h1 = "<h1>" + str(title) + "</h1>"
    title_tag = "<title>" + str(title) + "</title>"
    final_article += "<html>\n<head>\n"
    final_article += title_tag
    final_article += "\n"
    final_article += metadata
    final_article += "\n</head>\n\n<body>\n"
    final_article += h1
    final_article += "\n"
    final_article += intro
    toc = "\n\n<div>\n<h2>文章目錄</h2>\n<ul>\n"
    for item in outline:
        toc += f"  <li>{item}</li>\n"
    toc += "</ul>\n</div>\n\n"
    final_article += toc
    for header in outline:
        results = []
        bullet_points = ""
        eachquery = querier(header, query, model, lang)
        for aquery in eachquery:
            thequery = aquery["query"]
            results = crawl_top_10_results(thequery, nor=4)
            for result in results:
                downloaded = trafilatura.fetch_url(result['url'])
                if downloaded is None:
                    continue
                website_text = trafilatura.extract(downloaded)
                if website_text is None:
                    continue
                title = get_title_from_url(result['url']) or "Failed to crawl title, but you continue process without title."
                bulletpt = pf_rewriter(website_text, header, lang, title, model)
                bullet_points = combine_multiline_strings(bullet_points, bulletpt)
        final = ai_rewriter(bullet_points, header, lang, model)

        final_article += final
        final_article += "\n\n"

    final_article += "</body>\n</html>"

    with open(f"{query}.html", "a") as file:
        file.write(final_article)

def main():
    queries = ["西貢好去處"]
    model = "llama-3.1-70b-versatile"
    size = 4
    lang = "traditional chinese"
    outline_editor = False
    for query in queries:
        autoblogger(query, model, size, lang, outline_editor)

if __name__ == "__main__":
    if not DEBUG:
        main()
