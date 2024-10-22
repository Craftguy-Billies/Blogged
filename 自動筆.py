import trafilatura
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import pixabay.core
import ast
import json
import time
import random
import os
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring, parse, fromstring, ElementTree
from datetime import datetime
import urllib.parse
import pytz
import subprocess

hk_timezone = pytz.timezone('Asia/Hong_Kong')

DEBUG = False

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

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

def banner(title, model, outline = None, previous = None):
    data = ""
    again = ""
    if outline:
        data += "and the headers of the article:\n"
        data += str(outline)
        data += "\n\n"
        data += "make sure your returned query is in a different aspect, generate different results as the previous query:"
        data += previous

        again += "AGAIN: your returned query should be significantly different aspect from the previous query:"
        again += previous
    prompt = f"""
    i now have this blog title:
    {title}

    {data}

    now i want to download an image for this blog post. give me ONE search queries ONLY, in python list format.
    you should make the queries more long tail and detailed, but just do not exceed 100 characters.
    but make sure your query is to the point, not unrelated to the blog title.

    {again}
    
    output queries in english. output in a single dimensional python list format.
    No premable and explanations.
    """

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt.strip()}],
        temperature=0.2,
        top_p=0.7,
        max_tokens=8192,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content

    response = extract_list_content(response)[0]
    response = response[:97]
    px = pixabay.core("45631523-f41b44ca77fa2a2753db5e2d2")
    space = px.query(response, orientation = 'horizontal')

    with open('id.txt', 'r') as file:
        pic_ids = [line.strip() for line in file.readlines()]

    j = 0
    while True:
        pic_id = str(space[j].getId()).strip()
    
        if pic_id.lower() not in [pid.lower() for pid in pic_ids]:
            break
    
        j += 1

    with open('id.txt', 'a') as file:
        file.write(f'{pic_id}\n')

    image_dir = './images/'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
  
    if len(space) > 0:
        image = f'./images/{response}.jpg'
        dir = f'{response}.jpg'
        space[j].download(image, "largeImage")
    return dir

def titler(outline, query, model, lang, h2count, max_retries=3, delay=2):
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
	    if you add numbers like '7大', it MUST MATCH a general noun, such as 角度, 分析. DO NOT pair numbers with specific nouns that could be inaccurate based on article content.                  
            return me a single JSON object with single key 'title' without premable and explanations.
	    make the title no longer than 25 characters. but make sure the title include the complete keyword i want to optimize SEO for: {query}.
            you should SEO optimize the title with the keyword {query} naturally.
            output in {lang}
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
            article_title = article_title.replace("7", str(h2count))
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
            return me a python list of h2 headers. if there is no content, return an empty list
	    make sure your returned results are topics they focused, not AI created.
            each python list object MUST be quoted with double quotes.
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
            the h2 headers given should be distinct, non-repetitive, and focused. no generic or catch-all phrases. no need elaboration in headers if not mentioned in original header. DO NOT form headers by clustering other's multiple headers. i need PICK and REWRITE.
            my inner content will be slightly different from reference article, so make sure headers are reformed.
	    make sure the each headers are informational intent.
            quality should be prioritized, less headers are better than vague and overly broad headers. no generic or catch-all phrases.
            headers should be in {lang}
	    make sure the headers consist important keywords from the query {query}, like district names or particular nouns.
            DO NOT include any numbers in your headers.
            return me a python list of headers only.
            the python list MUST be quoted with double quotes.
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
            for example, 'shenzhen must go places' and 'shenzhen longhua district dessert shops' is having significantly different level of specificity. in this case, remove the bigger coverage one, i.e. 'shenzhen must go places'
            delete these vague or inappropriate headers ONLY. no need to modify acceptable headers.
            expected header count: {size}, filter the best headers i needed only.
            EVERY HEADER SHOULD BE DISTINCT ASPECT!
            output in {lang}
            return me a python list of h2 headers.
            the python list MUST be quoted with double quotes.
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
            craft the search query in {lang}. you should craft me at least two queries for the header.
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

def pf_rewriter(query, article, header, lang, title, url, model):
    full_article = ""
    datum = article.splitlines()
    firstlines = datum[:130]
    article = '\n'.join(firstlines)
    prompt = f"""
    title of the crawled article:
    {title}

    content of article:
    {article}

    i want to write paragraphs under the header {header}, and the full article's keyword is {query}
    first, validate is the country or information in the crawled article's URL: {url} matches the header {header} i want to write. discard the whole piece of article if it is unrelated (e.g. taiwan information in hong kong topic article). you can omit the latter steps if it is unrelated.
    if it is related, by seeing the title and content of article, understand the header is a noun or just a general concept. DO NOT misunderstand a general genre as a specific noun, as everything written will be wrong afterwards.
    generate me point forms for related information ONLY. do not give me related aspects.
    make sure your points are not just examples. return details and insights from the article.
    if the information i provided is referring to another service or information instead of the information looking for, return no results is better than wrong information.
    make sure you do not misidentify details. this is a MUST. make sure you did a summary check and ensure the bullet points are 100% correct without misidentifying events or information subject.
    be careful of wrong country, district, human names, if they match the header
    you MUST validate is the country or information in the crawled article's URL: {url} matches the header {header} i want to write. discard the whole piece of article if it is unrelated (e.g. taiwan information in hong kong topic article).
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

def ai_rewriter(query, bullet_points, header, lang, model):
    full_article = ""
    prompt = f"""
    {bullet_points}
    you are a helpful writing assistant, expertize in writing fluently and in a blogging tone.
    the main keyword for whole article is: {query}, and now i want to write paragraphs under this specific h2 header {header}.
    by seeing the bullet points, make sure you understand the header is a noun or just a general concept. DO NOT misunderstand a general genre as a specific noun, as everything written will be wrong afterwards.
    DO NOT GIVE INCONSISTANT INFORMATIONS! Comprehend the content and give me a consistent answer if there are two version of answers.
    you must only give me ONE <h2> in this reply.
    generate me paragraphs. you are not required to use every single information i provided, but make sure they are used fluently and appropriately.
    do not include promotions, and make sure the tone of rewriting is professional. make sure your returned paragraphs are coherent and fluent, instead of point form like paragraphs.
    your rewriting need to be humanized and fluent. prioritize fluency over informative.
    your replies must base on the web search information. do not create information.
    DO NOT INCLUDE INTRODUCTION AND CONCLUSION, OR RELATED ASPECTS. No "總而言之", "總之", "最後", "值得注意的是".
    make sure you do not misidentify details. this is a MUST.
    also return me details for each. DO NOT JUST KEEP GIVING EXAMPLES. I need details.
    return me in a HTML form. text must be labelled with html tags.
    you can add <h3> and <strong> if needed. but do not overuse <h3>.
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
    i want you to craft me an introductory paragraph that can captivate readers to continue reading. 
    Describe on what topics will be discussed in the following paragraphs. Word limit of the paragraph is 100 words.
    Starting with a question is preferred. Only use an exclamation mark at the last sentence.
    return me the introductory paragraph with <p> tags wrapped around.
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

def wrap_lines(multiline_string):
    lines = multiline_string.splitlines()
    wrapped_lines = []
    for line in lines:
        trimmed_line = line.strip()
        if not trimmed_line or (trimmed_line.startswith('<') and not trimmed_line.startswith('<strong>')):
            wrapped_lines.append(line)
        else:
            wrapped_line = f"<p>{trimmed_line}</p>"
            wrapped_lines.append(wrapped_line)
    return "\n".join(wrapped_lines)

def prettify_element(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def add_rss_item(template_path, link, blog):
    tree = parse(template_path)
    root = tree.getroot()
    channel = root.find('channel')
    last_build_date = channel.find('lastBuildDate')
    last_build_date.text = datetime.now(hk_timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
  
    soup = BeautifulSoup(blog, 'html.parser')
    title = soup.title.string
    enclosure_url = soup.find('img', class_='banner')['src']
    description = soup.find('div', class_='description').find('p').text

    # Create a new item
    item = Element('item')
    item_title = SubElement(item, 'title')
    item_title.text = title
    item_link = SubElement(item, 'link')
    item_link.text = link
    item_description = SubElement(item, 'description')
    item_description.text = description

    item_pub_date = SubElement(item, 'pubDate')
    item_pub_date.text = datetime.now(hk_timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
  
    root_url = "https://www.avoir.me"
    if enclosure_url.startswith(".."):
        enclosure_url = os.path.join(root_url, os.path.normpath(enclosure_url)[3:])
    if enclosure_url:
        item_enclosure = SubElement(item, 'enclosure', url=enclosure_url, type="image/jpeg")

    # Prettify the item
    pretty_item_str = prettify_element(item)
    pretty_item = fromstring(pretty_item_str.encode('utf-8'))
    channel.append(pretty_item)
    tree.write(template_path, encoding='utf-8', xml_declaration=True)

def add_blog_post(final_article, link, category):
    structure_file = "structure.json"
    # Load the existing structure
    if os.path.exists(structure_file):
        with open(structure_file, 'r') as file:
            structure = json.load(file)
    else:
        structure = {}

    # Navigate through categories and subcategories
    current_level = structure
    path = "category"
    for cat in category:
        if cat not in current_level:
            current_level[cat] = {}
        current_level = current_level[cat]
        path = os.path.join(path, cat)
        if not os.path.exists(path):
            os.makedirs(path)
            initialize_rss(path, cat)
    
    # Add the blog post to the category in the structure
    if 'posts' not in current_level:
        current_level['posts'] = []

    soup = BeautifulSoup(final_article, 'html.parser')
    title = soup.title.string
    enclosure_url = soup.find('img', class_='banner')['src']
    description = soup.find('div', class_='description').find('p').text

    root_url = "https://www.avoir.me"
    if enclosure_url.startswith(".."):
        enclosure_url = os.path.join(root_url, os.path.normpath(enclosure_url)[3:])

    pubdate = datetime.now(hk_timezone).strftime('%a, %d %b %Y %H:%M:%S %z')
    
    post = {
        'title': title,
        'link': link,
        'description': description,
        'enclosure': enclosure_url,
        'pubdate': pubdate
    }
    current_level['posts'].append(post)

    # Save the updated structure
    with open(structure_file, 'w') as file:
        json.dump(structure, file, indent=4)

    # Update RSS files for each level in the category hierarchy
    # Update for the main category
    main_category_path = os.path.join("category", category[0])
    main_rss_path = os.path.join(main_category_path, "rss.xml")
    update_rss(main_rss_path, post)

    # Update for the specific subcategory
    specific_rss_path = os.path.join(path, "rss.xml")
    if main_rss_path != specific_rss_path:  # Avoid double writing if it's the same path
        update_rss(specific_rss_path, post)


def initialize_rss(path, cat):
    """Initialize an RSS feed in a given directory."""
    rss_file = os.path.join(path, "rss.xml")
    channel = Element('channel')
    tree = ElementTree(channel)
    tree.write(rss_file, encoding='utf-8', xml_declaration=True)

    priority = "0.75"
    the_url = "https://www.avoir.me/" + path + "/"
    append_to_sitemap(the_url, priority)

    # category page content
    content = r"""<!DOCTYPE html>
                  <html lang="zh">
                  <head>
                  <meta charset="UTF-8">
                      <meta name="viewport" content="width=device-width, initial-scale=1.0">
		      <link rel="icon" href="https://www.avoir.me/icons/favicon.png" type="image/png">
                      <link rel="stylesheet" href="https://www.avoir.me/related_post.css">
                      <meta name="theme-color" content="white">
		      <link rel="icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
                      <link rel="shortcut icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
		      <link href="data:image/vnd.microsoft.icon;base64,AAABAAEAMDAAAAEAIACoJQAAFgAAACgAAAAwAAAAYAAAAAEAIAAAAAAAACQAAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAQOAICAvsEBATrJiYmFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAgIBwqKioSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////8AAP///////wAA////////AAD///////8AAP///////wAA////////AADAAP8AAAMAAMAA/wAAAwAAwAH/gAADAAD/D//w8P8AAP8P//Hx/wAA/4f/4eH/AAD/h//h4f8AAP/H/8PD/wAA/8P/w8P/AAD/w//Hx/8AAP/gAAAH/wAA/+AAAA//AAD/8AAAD/8AAP/w/w8P/wAA//j+Hh//AAD/+H4eH/8AAP/4fD4//wAA//w8PD//AAD//Dx8f/8AAP/+GHh//wAA//4YeH//AAD//xDw//8AAP//APD//wAA//8B8f//AAD//4Hh//8AAP//g+P//wAA///Dw///AAD//8PD//8AAP//44f//wAA///hh///AAD//+GP//8AAP//8A///wAA///wH///AAD///gf//8AAP//+B///wAA///8P///AAD///w///8AAP///n///wAA////////AAD///////8AAP///////wAA////////AAA=" rel="icon" type="image/x-icon">
                      <meta name="referrer" content="origin">
                      <meta property="og:locale" content="zh_TW" />
                      <meta property="og:site_name" content="Avoir" />
                      <link rel="stylesheet" href="https://fonts.googleapis.com/earlyaccess/notosanstc.css">
                      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"     integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                      <style> * {box-sizing: border-box;margin: 0;padding: 0;font-family: 'Noto Sans TC', sans-serif;scroll-behavior: smooth;}</style>
                      <title>"""
    content += "Avoir - " + cat + "</title>\n"

    # Dynamic data for the schema
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
	    {
	        "@type": "WebPage",
	        "name": cat,
	        "url": "https://www.avoir.me/" + path,
	        "description": cat
	    },
	    {
	        "@type": "Organization",
	        "name": "Avoir",
	        "url": "https://www.avoir.me",
		"logo": "https://www.avoir.me/icons/favicon.png",
	        "sameAs": [
		    "https://www.facebook.com/avoir.me",
		    "https://www.instagram.com/avoir.hk/",
		    "https://x.com/avoir_me"
	        ]
	    },
	    {
	      "@type": "WebSite",
	      "name": "Avoir",
	      "url": "https://www.avoir.me"
	    }
        ]
    }



    # Convert the dictionary to a JSON string
    schema_json = json.dumps(schema_data, indent=4)

    content += f"<script type='application/ld+json'>\n{schema_json}\n</script>"
    content += r"""
                    </head>
                    <body>
                    <nav>
                      <ul class = "sidebar" id = "content">
                          <li class = "xmark" onclick = hidesidebar()><a><i class="fa-solid fa-xmark"></i></a></li>
                          <div id="contain">
                              
                          </div>
                      </ul>
                      <ul id = "ts">
                          <li class = "Avoir-logo"><a href="https://www.avoir.me/">Avoir</a></li>
                          <li class = "hideOnMobile dropdown">
                              <a href="https://www.avoir.me/related_post.html">最新推薦</a>
                              <div class="dropdownmenu">
                                  <div class="first-box2">
              
                                  </div>
                              </div>
                          </li>
                          <li class = "menu-button" onclick = showsidebar()><a><i class="fa-solid fa-bars"></i></a></li>
                      </ul>
                  </nav>
                  <div class="recommended" id="recommended">
                      <div class="direct">"""
    categories = path.split('/')[1:]
    current_path = "category/"
    base_url = "https://www.avoir.me/"
    content += '<a href="https://www.avoir.me/">Home</a>'
    for cate in categories:
      current_path += cate + '/'  # Append category to the current path
      content += ' <i class="fa-solid fa-angle-right"></i> <a href="' + base_url + current_path + '">' + cate + '</a>'
    content += r"""</div>
                    <div class="recommend">"""
    content += cat
    content += r"""       </div>
                          <div class="line"></div>
                      </div>
                      <footer>
                        <div class="footerContainer">
                            <div class="socialIcons">
                                <a href="mailto:billy@avoir.me"><i class="fa-solid fa-envelope"></i></a>
			        <a href="https://www.instagram.com/avoir.hk/"><i class="fa-brands fa-instagram"></i></a>
	   			<a href="https://www.facebook.com/avoir.me"><i class="fa-brands fa-facebook"></i></a>
			        <a href="https://x.com/avoir_me"><i class="fa-brands fa-x-twitter"></i></a>
                            </div>
                            <div class="footer-nav">
                                <ul id="footerCategories">
                                    <li><a href="https://www.avoir.me">主頁</a></li>
                                </ul>
                            </div>
                        </div>
                        <div class="footer-bottom">
                            <p>Copyright &copy; 2024 by <span class="highlight">Avoir.me</span> All Rights Reserved.</p>
                        </div>
                    </footer>
                  <script src="https://www.avoir.me/related_post.js"></script>
		  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1588758681130963"
     crossorigin="anonymous"></script>
                  </body>
                  </html>
                  """

    # Create HTML file
    html_file = os.path.join(path, "index.html")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(content)


def prettify(element, level=0):
    """Return a pretty-printed XML string for the Element."""
    indent = "\n" + level * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indent + "  "
        if not element.tail or not element.tail.strip():
            element.tail = indent
        for elem in element:
            prettify(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
    else:
        if level and (not element.tail or not element.tail.strip()):
            element.tail = indent

def update_rss(rss_path, post):
    """Update the RSS file with a new blog post, prettifying the XML."""
    if os.path.exists(rss_path):
        tree = ElementTree(file=rss_path)
        channel = tree.getroot()
    else:
        channel = Element('channel')
        tree = ElementTree(channel)

    item = SubElement(channel, 'item')
    SubElement(item, 'title').text = post['title']
    SubElement(item, 'link').text = post['link']
    SubElement(item, 'description').text = post['description']
    SubElement(item, 'enclosure', url=post['enclosure'], type="image/jpeg")
    SubElement(item, 'pubDate').text = post['pubdate']

    # Prettify the entire XML tree
    prettify(channel)

    tree.write(rss_path, encoding='utf-8', xml_declaration=True)

def append_to_sitemap(loc, priority):
    # File path to the sitemap.xml
    file_path = 'sitemap.xml'

    # Parse the existing sitemap.xml file
    tree = parse(file_path)
    root = tree.getroot()

    # Declare the sitemap namespace
    sitemap_ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    nsmap = {"ns0": sitemap_ns}

    # Create a new <url> element in the sitemap namespace
    new_url = Element(f"{{{sitemap_ns}}}url")

    # Add <loc> element
    loc_element = SubElement(new_url, f"{{{sitemap_ns}}}loc")
    loc_element.text = loc

    # Add <lastmod> element with the current time in Hong Kong timezone
    hk_timezone = pytz.timezone('Asia/Hong_Kong')
    current_time = datetime.now(hk_timezone)
    lastmod_element = SubElement(new_url, f"{{{sitemap_ns}}}lastmod")
    lastmod_element.text = current_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    lastmod_element.text = lastmod_element.text[:-2] + ':' + lastmod_element.text[-2:]

    # Add <changefreq> element
    changefreq_element = SubElement(new_url, f"{{{sitemap_ns}}}changefreq")
    changefreq_element.text = "weekly"

    # Add <priority> element
    priority_element = SubElement(new_url, f"{{{sitemap_ns}}}priority")
    priority_element.text = priority

    # Append the new <url> element to the root <urlset> element
    root.append(new_url)

    # Internal prettify function with a different name
    def prettify_xml_tree(element, level=0):
        """Prettifies the XML tree in place by adding indentation and newlines."""
        indent = "\n" + level * "  "
        if len(element):  # If the element has children
            if not element.text or not element.text.strip():
                element.text = indent + "  "
            for elem in element:
                prettify_xml_tree(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
        else:
            if not element.text or not element.text.strip():
                element.text = ""
            if level and (not element.tail or not element.tail.strip()):
                element.tail = indent

    prettify_xml_tree(root)  # Call the renamed prettify function

    # Write the updated and prettified XML back to the file
    tree = ElementTree(root)
    tree.write(file_path, encoding='UTF-8', xml_declaration=True)

def get_current_hk_time():
    tz_hk = pytz.timezone('Asia/Hong_Kong')
    current_time = datetime.now(tz_hk)
    return current_time.isoformat()

def commit_changes():
    try:
        # Step 1: Set Git config to always merge changes (avoids rebase conflicts)
        subprocess.run(["git", "config", "pull.rebase", "false"], check=True)

        # Step 2: Fetch the latest changes from GitHub
        subprocess.run(["git", "fetch", "origin"], check=True)
        
        # Step 3: Add all local changes
        subprocess.run(["git", "add", "--all"], check=True)
        
        # Step 4: Commit local changes
        subprocess.run(["git", "commit", "-m", "讀萬卷書不如寫萬篇文"], check=True)
        
        # Step 5: Pull the latest changes from GitHub and merge
        subprocess.run(["git", "pull", "--strategy=recursive", "--strategy-option=theirs"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error occurred during git operation: {e}")
        # Continue even if pull fails due to conflicts

    try:
        # Step 6: Push the changes, force if needed
        subprocess.run(["git", "push", "--force"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during git push: {e}")


def autoblogger(query, model, size, lang, category, sample_size, outline_editor):
    outline = headerizer(structurer(crawl_top_10_results(query), query, model), query, model, lang, size)
    if outline_editor:
      outline = outline_editing(outline)
    final_article = "<!DOCTYPE html>"
    h2count = len(outline)
    title = titler(outline, query, model, lang, h2count)
    file_url = f"https://avoir.me/{query}/index.html"
    ban = banner(title, model)
    image = banner(title, model, outline, ban)
    metadata = metadataer(outline, query, lang, model)
    intro = introer(outline, title, lang, model)
    h1 = "<h1>" + str(title) + "</h1>"
    title_tag = "<title>" + str(title) + "</title>"
    final_article += "<html>\n<head>\n"
    final_article += title_tag
    final_article += "\n"
    final_article += metadata
    final_article += '\n'
    final_article += '<link rel="canonical" href="https://www.avoir.me/' + query + '/">'

    # Variables for the meta content
    og_url = "https://www.avoir.me/" + query + "/"
    og_title = query
    souper = BeautifulSoup(intro, 'html.parser')
    le_intro = souper.find_all('p')
    og_description = le_intro[0].get_text() if le_intro else None
    og_image = "https://www.avoir.me/images/" + ban

    # Dynamically construct the meta tags
    meta_tags = f'''
    <meta property="og:url" content="{og_url}" />
    <meta property="og:title" content="{og_title}" />
    <meta property="og:description" content="{og_description}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:title" content="{og_title}" />
    <meta property="twitter:description" content="{og_description}" />
    <meta property="twitter:image" content="{og_image}" />
    '''

    final_article += meta_tags
    final_article += r'''<link rel="stylesheet" href="https://www.avoir.me/post.css">
    			<link rel="icon" href="https://www.avoir.me/icons/favicon.png" type="image/png">
                        <meta name="theme-color" content="white">
			<link href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEjSURBVFhH5ZXdDYMwDIRJR2AA5mUAdmAdnhmAF4QYoW2iXBtZiX8CCFX9JOSUEp99OMI93zQ38ojxNn67AOdcuI7wuw6knU/TFFd2qk8Btb72MFU5sK5riF706CmucgDdYyv9baF6BlKxGmFgLoA7dtx/JU45BZ62bePKhqkAiM7zHGLKtm0hDsMQohbTEKbDlq5B7p6E2oFlWULkkluEgdqBUsd0u9UF0wzkkkIQaIWBqgAqAjix0h6K2oEzxHKIBUjJ932Pqy8otu/7EDnEITzSnUdIzzswjmOIPgl3gdJ9DtYBdK9J5p+lz2n2izOgEQf0dWn2FguwvntOjMvFOmDpHlCxruviKs9nBqSOazssgXziDFyN6XN8Bbc78O8FNM0Lp5u30Y5sbbYAAAAASUVORK5CYII=" rel="icon" type="image/x-icon">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <link rel="stylesheet" href="https://fonts.googleapis.com/earlyaccess/notosanstc.css">
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"     integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                        <meta property="og:locale" content="zh_TW" />
                        <meta property="og:site_name" content="Avoir" />
	                <meta property="og:type" content="article" />
		 	<meta name="robots" content="index, follow" />
		 	<meta name="author" content="Avoir" />
                        <meta name="referrer" content="origin">
			<meta name="apple-mobile-web-app-capable" content="yes"/>
                        <meta name="apple-mobile-web-app-status-bar-style" content="black"/>
                        <meta name="apple-mobile-web-app-title" content="Avoir"/>
                        <meta name="apple-touch-fullscreen" content="yes"/>
			<link rel="icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
                        <link rel="shortcut icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
                        <style> * {box-sizing: border-box;margin: 0;padding: 0;font-family: 'Noto Sans TC', sans-serif;scroll-behavior: smooth;}</style>'''
	
    # Dynamic data for the schema
    schema_data = {
        "@context": "https://schema.org",
        "@graph": [
	    {
	      "@type": "Article",
	      "headline": title,
	      "description": intro,
	      "url": og_url,
	      "image": og_image,
	      "datePublished": get_current_hk_time(),
	      "author": {
	          "@type": "Person",
	          "name": "Avoir"
	      },
	      "publisher": {
	          "@type": "Organization",
	          "name": "Avoir",
	          "url": "https://www.avoir.me"
	      }
            },
	    {
	      "@type": "Organization",
	      "name": "Avoir",
	      "url": "https://www.avoir.me",
	      "logo": "https://www.avoir.me/icons/favicon.png",
	      "sameAs": [
	          "https://www.facebook.com/avoir.me",
		  "https://www.instagram.com/avoir.hk/",
		  "https://x.com/avoir_me"
	      ]
	    },
	    {
	      "@type": "WebSite",
	      "name": "Avoir",
	      "url": "https://www.avoir.me"
	    }
	]
    }

    # Convert the dictionary to a JSON string
    schema_json = json.dumps(schema_data)

    final_article += f"<script type='application/ld+json'>{schema_json}</script>"
    final_article += '\n</head>\n\n<body>\n'
    final_article += r'''<nav>
                              <ul class = "sidebar" id = "content">
                                  <li class = "xmark" onclick = hidesidebar()><a><i class="fa-solid fa-xmark"></i></a></li>
                                  <div id="contain">
                                      
                                  </div>
                              </ul>
                              <ul id = "ts">
                                  <li class = "Avoir-logo"><a href="https://www.avoir.me/">Avoir</a></li>
                                  <li class = "hideOnMobile dropdown">
                                      <a href="https://www.avoir.me/related_post.html">最新推薦</a>
                                      <div class="dropdownmenu">
                                          <div class="first-box2">
                      
                                          </div>
                                      </div>
                                  </li>
                                  <li class = "menu-button" onclick = showsidebar()><a><i class="fa-solid fa-bars"></i></a></li>
                              </ul>
                          </nav>'''
    final_article += '\n<img class="banner" src="../images/'
    final_article += ban
    final_article += '">\n<div class="direct">\n  <a href="https://www.avoir.me/">Home</a>\n'
    cat_url = "/category/"
    for cat in category:
      cat_url += cat + '/'
      final_article += '  <i class="fa-solid fa-angle-right"></i> <a href="https://www.avoir.me' + cat_url + '">' + cat + '</a>'
    final_article += "\n</div>\n"
    final_article += '<div class="blog-type">'
    final_article += category[0]
    final_article += '</div>'
    final_article += h1
    final_article += '\n<div class = "description">'
    final_article += intro
    final_article += '\n</div>\n'
    hong_kong_tz = pytz.timezone('Asia/Hong_Kong')
    current_time = datetime.now(hong_kong_tz)
    formatted_date = current_time.strftime('%d %b %Y')
    author_name = "Avoir"
    publish_date_html = f'<div class="publish-date">By {author_name} - {formatted_date}</div>'
    final_article += publish_date_html
    toc = '\n\n<section class="middle-img">\n<figure>\n<img class = "middle-img-edit" src="../images/'
    toc += image
    toc += '">\n<figcaption>Image Source: Pixabay</figcaption></figure>\n</section>\n\n<div class="content-page">\n<h2>文章目錄</h2>\n<ul>\n'
    for item in outline:
        toc += f"  <li>{item}</li>\n"
    toc += '</ul>\n</div>\n\n<div class"main">\n'
    final_article += toc
    for header in outline:
        results = []
        bullet_points = ""
        eachquery = querier(header, query, model, lang)
        for aquery in eachquery:
            thequery = aquery["query"]
            results = crawl_top_10_results(thequery, nor=sample_size)
            for result in results:
                downloaded = trafilatura.fetch_url(result['url'])
                if downloaded is None:
                    continue
                website_text = trafilatura.extract(downloaded)
                if website_text is None:
                    continue
                title = get_title_from_url(result['url']) or "Failed to crawl title, but you continue process without title."
                bulletpt = pf_rewriter(query, website_text, header, lang, title, result['url'], model)
                bullet_points = combine_multiline_strings(bullet_points, bulletpt)
                bullet_points += f"\nNext Article, title: {title}, url: {result['url']}\n"
        final = ai_rewriter(query, bullet_points, header, lang, model)

        final_article += final
        final_article += "\n\n"

    final_article = wrap_lines(final_article)
    final_article += r"""
                      <br>
                      <div class="recommended" id="recommended">
                        <div class="recommend">
                            延伸閱讀
                        </div>
                        <div class="line"></div>
                      </div>
                      <footer>
                          <div class="footerContainer">
                              <div class="socialIcons">
                                  <a href="mailto:billy@avoir.me"><i class="fa-solid fa-envelope"></i></a>
                                  <a href="https://www.instagram.com/avoir.hk/"><i class="fa-brands fa-instagram"></i></a>
				  <a href="https://www.facebook.com/avoir.me"><i class="fa-brands fa-facebook"></i></a>
                                  <a href="https://x.com/avoir_me"><i class="fa-brands fa-x-twitter"></i></a>
                              </div>
                              <div class="footer-nav">
                                  <ul id="footerCategories">
                                      <li><a href="https://www.avoir.me">主頁</a></li>
                                  </ul>
                              </div>
                          </div>
                          <div class="footer-bottom">
                              <p>Copyright &copy; 2024 by <span class="highlight">Avoir.me</span> All Rights Reserved.</p>
                          </div>
                      </footer>
                  <script src="https://www.avoir.me/post.js"></script>
		  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1588758681130963"
     crossorigin="anonymous"></script>
    """
    final_article += "\n</div>\n</body>\n</html>"
    dir_path = query
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "index.html")
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(final_article)

    encoded_url = urllib.parse.quote(file_url, safe=':/')
    add_rss_item("rss.xml", encoded_url, final_article)
    add_blog_post(final_article, encoded_url, category)
    loc = "https://www.avoir.me/"
    loc += query
    loc += "/"
    priority = "0.90"
    append_to_sitemap(loc, priority)
    commit_changes()
	

def main():
    queries = ["容易長肌肉的體質"
]
    categories = [['健康', '運動']]
    model = "meta/llama-3.1-405b-instruct"
    size = 4
    sample_size = 4
    lang = "traditional chinese, MUST also convert ALL simplified chinese to traditional"
    outline_editor = False
    for query, category in zip(queries, categories):
        autoblogger(query, model, size, lang, category, sample_size, outline_editor)

if __name__ == "__main__":
    if not DEBUG:
        main()
