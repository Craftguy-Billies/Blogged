import asyncio
from openai import OpenAI
from bs4 import BeautifulSoup
import requests
import ast
import os
import json
import urllib.parse

model = "meta/llama-3.1-405b-instruct"

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "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"
)

blogs = [r"""


<!DOCTYPE html><html>
<head>
<title>淘寶信用卡付款手續費大解密：3大關鍵點盤點，教你聰明省錢</title>
<meta name="description" content="了解淘寶信用卡付款手續費的解析、回饋機制詳解及手續費與匯率的關係，讓你淘寶購物更划算。">

<meta name="keywords" content="淘寶信用卡付款手續費, 淘寶信用卡回饋機制, 淘寶信用卡手續費, 匯率, 淘寶購物, 信用卡付款">
<link rel="canonical" href="https://www.avoir.me/淘寶信用卡付款手續費/">
    <meta property="og:url" content="https://www.avoir.me/淘寶信用卡付款手續費/" />
    <meta property="og:title" content="淘寶信用卡付款手續費" />
    <meta property="og:description" content="[<p>你是否曾經在淘寶上購物時，忽略了信用卡付款手續費的存在？你是否知道，這些看似微不足道的手續費，竟然可以吃掉你一大筆的消費回饋？想知道淘寶信用卡付款手續費的真相嗎？本文將為你揭露3大關鍵點，教你如何聰明地省錢！</p>]" />
    <meta property="og:image" content="https://www.avoir.me/images/Credit card payment fees.jpg" />
    <meta property="twitter:card" content="summary_large_image" />
    <meta property="twitter:title" content="淘寶信用卡付款手續費" />
    <meta property="twitter:description" content="[<p>你是否曾經在淘寶上購物時，忽略了信用卡付款手續費的存在？你是否知道，這些看似微不足道的手續費，竟然可以吃掉你一大筆的消費回饋？想知道淘寶信用卡付款手續費的真相嗎？本文將為你揭露3大關鍵點，教你如何聰明地省錢！</p>]" />
    <meta property="twitter:image" content="https://www.avoir.me/images/Credit card payment fees.jpg" />
    <link rel="stylesheet" href="https://www.avoir.me/post.css">
    			<link rel="icon" href="https://www.avoir.me/icons/favicon.png" type="image/png">
                        <meta name="theme-color" content="white">
			<link href="data:image/vnd.microsoft.icon;base64,AAABAAEAMDAAAAEAIACoJQAAFgAAACgAAAAwAAAAYAAAAAEAIAAAAAAAACQAAMMOAADDDgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEBAQOAICAvsEBATrJiYmFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAgIBwqKioSAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD///////8AAP///////wAA////////AAD///////8AAP///////wAA////////AADAAP8AAAMAAMAA/wAAAwAAwAH/gAADAAD/D//w8P8AAP8P//Hx/wAA/4f/4eH/AAD/h//h4f8AAP/H/8PD/wAA/8P/w8P/AAD/w//Hx/8AAP/gAAAH/wAA/+AAAA//AAD/8AAAD/8AAP/w/w8P/wAA//j+Hh//AAD/+H4eH/8AAP/4fD4//wAA//w8PD//AAD//Dx8f/8AAP/+GHh//wAA//4YeH//AAD//xDw//8AAP//APD//wAA//8B8f//AAD//4Hh//8AAP//g+P//wAA///Dw///AAD//8PD//8AAP//44f//wAA///hh///AAD//+GP//8AAP//8A///wAA///wH///AAD///gf//8AAP//+B///wAA///8P///AAD///w///8AAP///n///wAA////////AAD///////8AAP///////wAA////////AAA=" rel="icon" type="image/x-icon">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <link rel="stylesheet" href="https://fonts.googleapis.com/earlyaccess/notosanstc.css">
                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css"     integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
                        <meta property="og:locale" content="zh_TW" />
                        <meta property="og:site_name" content="Avoir" />
	                <meta property="og:type" content="article" />
		 	<meta name="robots" content="index, follow" />
		 	<meta name="author" content="Avoir" />
                        <meta name="referrer" content="origin">
			<link rel="icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
                        <link rel="shortcut icon" type="image/x-icon" href="https://www.avoir.me/icons/favicon.ico">
                        <style> * {box-sizing: border-box;margin: 0;padding: 0;font-family: 'Noto Sans TC', sans-serif;scroll-behavior: smooth;}</style><script type='application/ld+json'>{"@context": "https://schema.org", "@graph": [{"@type": "Article", "headline": "\u6dd8\u5bf6\u4fe1\u7528\u5361\u4ed8\u6b3e\u624b\u7e8c\u8cbb\u5927\u89e3\u5bc6\uff1a3\u5927\u95dc\u9375\u9ede\u76e4\u9ede\uff0c\u6559\u4f60\u8070\u660e\u7701\u9322", "description": "<p>\u4f60\u662f\u5426\u66fe\u7d93\u5728\u6dd8\u5bf6\u4e0a\u8cfc\u7269\u6642\uff0c\u5ffd\u7565\u4e86\u4fe1\u7528\u5361\u4ed8\u6b3e\u624b\u7e8c\u8cbb\u7684\u5b58\u5728\uff1f\u4f60\u662f\u5426\u77e5\u9053\uff0c\u9019\u4e9b\u770b\u4f3c\u5fae\u4e0d\u8db3\u9053\u7684\u624b\u7e8c\u8cbb\uff0c\u7adf\u7136\u53ef\u4ee5\u5403\u6389\u4f60\u4e00\u5927\u7b46\u7684\u6d88\u8cbb\u56de\u994b\uff1f\u60f3\u77e5\u9053\u6dd8\u5bf6\u4fe1\u7528\u5361\u4ed8\u6b3e\u624b\u7e8c\u8cbb\u7684\u771f\u76f8\u55ce\uff1f\u672c\u6587\u5c07\u70ba\u4f60\u63ed\u97323\u5927\u95dc\u9375\u9ede\uff0c\u6559\u4f60\u5982\u4f55\u8070\u660e\u5730\u7701\u9322\uff01</p>", "url": "https://www.avoir.me/\u6dd8\u5bf6\u4fe1\u7528\u5361\u4ed8\u6b3e\u624b\u7e8c\u8cbb/", "image": "https://www.avoir.me/images/Credit card payment fees.jpg", "datePublished": "2024-09-19T15:51:40.009801+08:00", "author": {"@type": "Person", "name": "Avoir"}, "publisher": {"@type": "Organization", "name": "Avoir", "url": "https://www.avoir.me"}}, {"@type": "Organization", "name": "Avoir", "url": "https://www.avoir.me", "logo": "https://www.avoir.me/icons/favicon.png", "sameAs": ["https://www.facebook.com/avoir.me", "https://www.instagram.com/avoir.hk/", "https://x.com/avoir_me"]}, {"@type": "WebSite", "name": "Avoir", "url": "https://www.avoir.me"}]}</script>
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
<img class="banner" src="../images/Credit card payment fees.jpg">
<div class="direct">
  <a href="https://www.avoir.me/">Home</a>
  <i class="fa-solid fa-angle-right"></i> <a href="https://www.avoir.me/category/購物/">購物</a>  <i class="fa-solid fa-angle-right"></i> <a href="https://www.avoir.me/category/購物/網上購物/">網上購物</a>
</div>
<div class="blog-type">購物</div><h1>淘寶信用卡付款手續費大解密：3大關鍵點盤點，教你聰明省錢</h1>
<div class = "description"><p>你是否曾經在淘寶上購物時，忽略了信用卡付款手續費的存在？你是否知道，這些看似微不足道的手續費，竟然可以吃掉你一大筆的消費回饋？想知道淘寶信用卡付款手續費的真相嗎？本文將為你揭露3大關鍵點，教你如何聰明地省錢！</p>
</div>
<div class="publish-date">By Avoir - 19 Sep 2024</div>

<section class="middle-img">
<figure>
<img class = "middle-img-edit" src="../images/Online shopping transaction fees.jpg">
<figcaption>Image Source: Pixabay</figcaption></figure>
</section>

<div class="content-page">
<h2>文章目錄</h2>
<ul>
  <li>淘寶信用卡付款手續費解析</li>
  <li>淘寶信用卡回饋機制詳解</li>
  <li>淘寶信用卡手續費與匯率的關係</li>
</ul>
</div>

<div class"main">
<h2>淘寶信用卡付款手續費解析</h2>

<p>淘寶信用卡付款手續費是指在淘寶平台上使用信用卡進行付款時，需要支付的一筆手續費。這筆手續費的收取方是淘寶的合作銀行，費率一般為交易金額的1%至3%不等。另外，信用卡國外手續費也會被收取，通常為1.5%。因此，總計手續費為4.5%。</p>

<p>除了信用卡付款手續費外，使用ATM轉帳功能付款僅需負擔1%的手續費，但跨行轉帳手續費可能會被收取。超商付款手續費為NT$15 + 1%，而支付寶儲值手續費為5%。台灣Pay手續費為1.5% + 1% = 2.5%。</p>

<h3>信用卡手續費</h3>

<p>Visa/Mastercard信用卡手續費為3%，而支付寶HK（餘額支付）手續費為1%。支付寶HK（中銀信用卡）手續費為1.2%，而支付寶HK（其他信用卡）手續費為1.5%。中銀淘寶World萬事達卡手續費為0%，而渣打Q Credit Card每月首5筆交易免手續費，之後每筆交易1.5%手續費。</p>

<p>信用卡手續費的收取方式是根據交易金額為基礎，按一定比例收取。買家或賣家承擔手續費，視具體情況而定。部分信用卡或支付渠道有特定的免手續費條件。另外，退款時，7日內退回到信用卡帳戶，若購買30天內退款，3%手續費可退回，銀行另收的1%~1.5%手續費依銀行規定辦理。</p>

<h2>淘寶信用卡回饋機制詳解</h2>

<p>淘寶信用卡回饋機制主要分為兩部分：基本回饋和加碼回饋。基本回饋通常為1%至3%，視信用卡發卡銀行和卡別而定。加碼回饋則依據信用卡的特定優惠活動而定，例如指定通路消費、海外消費等。</p>

<p>部分信用卡需要滿足特定條件才能享有加碼回饋，例如消費金額、消費次數等。例如，永豐SPORT卡需要單筆消費滿3,000元以上才能享有最高7%的豐點回饋。另外，部分信用卡的網購回饋不包括經AlipayHK的交易，需注意回饋條款。</p>

<p>淘寶信用卡回饋率會因卡片類型和支付方式而異。例如，滙豐Live+現金回饋卡的回饋率最高可達4.88%，而永豐SPORT卡的回饋率最高可達7%。此外，部分信用卡公司提供海外消費回饋，例如永豐幣倍卡（最高3%現金回饋）、彰銀My購卡（海外網購享6%現金回饋）。 </p>

<p>淘寶信用卡回饋機制可能會有變動，需注意最新的活動內容和條件。另外，信用卡公司與淘寶合作推出加碼活動，例如滿額贈、現金回饋加碼等。部分信用卡提供紅利點數回饋，例如聯邦賴點卡（指定網購享LINE POINTS 3%回饋）。 </p>

<p>最後，淘寶信用卡回饋機制需考慮手續費和回饋率兩個因素。部分信用卡的回饋率可能不足以cover手續費，需注意回饋條款和手續費收費方式。例如，Visa/Mastercard直接俾錢需收3%手續費 + 1.95%外幣手續費。 </p>

<h2>淘寶信用卡手續費與匯率的關係</h2>

<p>淘寶信用卡手續費是指使用信用卡在淘寶平台進行交易時，需要支付的一筆手續費。根據淘寶的規定，信用卡手續費一般為交易金額的3%。然而，這筆手續費並不是唯一的費用，因為信用卡公司可能會收取額外的國際交易手續費，通常為1.5%。</p>

<p>匯率是指信用卡公司將交易金額從人民幣轉換成港幣或新台幣的匯率。這個匯率會影響信用卡手續費的計算，因為信用卡公司會根據匯率將交易金額轉換成相應的貨幣，然後計算手續費。因此，匯率的變動會間接影響信用卡手續費的金額。</p>

<p>值得注意的是，信用卡公司的匯率可能與實際市場匯率有所差異。這意味著，即使交易金額相同，不同的信用卡公司可能會收取不同的匯率，從而導致手續費的金額不同。因此，使用者需要注意信用卡公司的匯率政策，以避免不必要的費用。</p>

<p>另外，部分信用卡公司可能會提供優惠匯率或豁免匯率轉換費用。這些優惠可以幫助使用者節省手續費，特別是在進行大額交易時。然而，這些優惠可能會受到信用卡公司的條款和條件限制，因此使用者需要仔細閱讀信用卡公司的政策，以確保自己能夠享受這些優惠。</p>

<p>總的來說，淘寶信用卡手續費與匯率的關係是密不可分的。使用者需要注意信用卡公司的匯率政策和手續費率，以避免不必要的費用。同時，也需要注意信用卡公司的優惠政策，以節省手續費。</p>

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
                                  <a href="/cdn-cgi/l/email-protection#187a7174746158796e77716a36757d"><i class="fa-solid fa-envelope"></i></a>
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
                  <script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script><script src="https://www.avoir.me/post.js"></script>
    
</div>
<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;if(b){var d=b.createElement('script');d.innerHTML="window.__CF$cv$params={r:'8c5f0d006b5a04bf',t:'MTcyNjgwNjMxOC4wMDAwMDA='};var a=document.createElement('script');a.nonce='';a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';document.getElementsByTagName('head')[0].appendChild(a);";b.getElementsByTagName('head')[0].appendChild(d)}}if(document.body){var a=document.createElement('iframe');a.height=1;a.width=1;a.style.position='absolute';a.style.top=0;a.style.left=0;a.style.border='none';a.style.visibility='hidden';document.body.appendChild(a);if('loading'!==document.readyState)c();else if(window.addEventListener)document.addEventListener('DOMContentLoaded',c);else{var e=document.onreadystatechange||function(){};document.onreadystatechange=function(b){e(b);'loading'!==document.readyState&&(document.onreadystatechange=e,c())}}}})();</script><script defer src="https://static.cloudflareinsights.com/beacon.min.js/vcd15cbe7772f49c399c6a5babf22c1241717689176015" integrity="sha512-ZpsOmlRQV6y907TI0dKBHq9Md29nnaEIPlkf84rnaERnq6zvWvPUqr2ft8M1aS28oN72PdrCzSjY4U6VaAw1EQ==" data-cf-beacon='{"rayId":"8c5f0d006b5a04bf","version":"2024.8.0","r":1,"token":"e2c7b19909e14b5c88fd46f23df1b50e","serverTiming":{"name":{"cfExtPri":true,"cfL4":true}}}' crossorigin="anonymous"></script>
</body>
</html>
"""]

with open("results.txt", "w", encoding="utf-8") as file:
    file.write("")

def extract_body(blog):
    html_content = blog
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the body tag
    body = soup.find('body')
    
    # Extract the entire body content as a string
    body_content = str(body) if body else ""
    
    # Return the body content as a JSON object
    return json.dumps({'body': body_content}, indent=4)

def extract_headers_and_paragraphs(blog):
    html_content = blog
    soup = BeautifulSoup(html_content, "html.parser")
    content_list = []
    elements = soup.find_all(['h2', 'h3', 'p'])
    current_header = None
    current_paragraphs = []
    first_pair = True
    for element in elements:
        if element.name in ['h2', 'h3']:
            if current_header is not None:
                if not first_pair:
                    merged_paragraphs = ' '.join(current_paragraphs)
                    content_list.append({
                        'header': f"<{element.name}>{current_header}</{element.name}>",
                        'paragraphs': merged_paragraphs
                    })
                else:
                    first_pair = False
            current_header = element.get_text()
            current_paragraphs = []
        elif element.name == 'p':
            if current_header is not None:
                current_paragraphs.append(element.get_text())
    if current_header is not None and not first_pair:
        merged_paragraphs = ' '.join(current_paragraphs)
        content_list.append({
            'header': f"<{element.name}>{current_header}</{element.name}>",
            'paragraphs': merged_paragraphs
        })

    return content_list

def converter(hnp):
    prompt = f"""
    i now have this header and this paragraph:
    {hnp}

    in my blog post.
    now i want to convert them into an instagram post format, which simply does humanization and summarization for the paragraph ONLY, and make the header CONCISE and SHORT (less than 10 chinese characters).
    return me plain text format to wrap the concise version of header (just for formatting), and the rewritten paragraph. The paragraph should be around 200-300 chinese characters ONLY.
    the paragraph should be in point form.
    the rewritten paragraph is NOT PROMOTIONAL but informational. USE THRID PERSON NARRATIVE. use friendly and professional tone. Do not include introductions, conclusions and promotions, but ONLY TO THE POINT.
    the headers should be wrapped with emojis if possible. 
    the paragraph should be in point form.
    no bold font is needed.
    No premable and explanations.
    REMEMBER: No premable and explanations!
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

    return response

def hashtagger(t):
    prompt = f"""
    i now have this blog post body.
    {t}

    i want you to generate me 5 hashtags for instagram posts. make sure the hashtags are closely relevant to the blog post content.
    the hashtags must be in traditional chinese.
    return me the hashtags only without premable and explanations.

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

    return response

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

ig = ""
fb = []
for blog in blogs:
    soup = BeautifulSoup(blog, 'html.parser')
    canonical_link_tag = soup.find('link', rel='canonical')
    if canonical_link_tag and 'href' in canonical_link_tag.attrs:
        canonical_url = canonical_link_tag['href']
        canonical_url = urllib.parse.quote(canonical_url)
    h1_tag = soup.find('h1')
    if h1_tag:
        h1_content = h1_tag.text.strip()
    blog_type_div = soup.find('div', class_='blog-type')
    if blog_type_div:
        blog_type_content = blog_type_div.text.strip()
    hnp = extract_headers_and_paragraphs(blog)
    t = hashtagger(extract_body(blog))
    for ehnp in hnp:
        thnp = converter(ehnp)
        fb.append(thnp)
        fb.append("\n\n")

for b in fb:
    ig += b

ig += "\n"
ig += "原文網址: " + canonical_url

ig += "\n\n"
ig += "Tags: " + t
ig += "\n\n"

ig += "=======================  輔助元素 ======================="
ig += "\n" 
ig += "分類: " + blog_type_content
ig += "\n"
ig += "標題: " + h1_content
ig += "\n\n\n\n\n\n"

with open("results.txt", "a", encoding="utf-8") as file:
    file.write(ig)
