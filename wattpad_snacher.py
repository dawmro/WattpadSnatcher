from datetime import datetime
import os
import re
import time
from os import close
from playwright.sync_api import sync_playwright



if not os.path.exists("chapters"):
        os.makedirs("chapters") 
        
        
def showTime():
    return str("["+datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+" UTC]")       
        
        
# To make sure the entire chapter is loaded, wait for page to load at the top of page and press page down multiple times to get to the bottom.
def press_page_down(page, how_many_times: int = 80 , debug: bool = False):
    for scroll_loop in range(how_many_times):
        page.keyboard.press("PageDown")
        time.sleep(0.2)
        try:
            page.wait_for_load_state(state='load', timeout=5000)
        except:
            print("not idle for 3 seconds")
        if debug:
            print(f"{showTime()} scroll_loop: {scroll_loop}")

        
        
# Remove symbols that are illegal for directory name
def remove_illegal_symbols(chapter_title):
    chapter_title_cleaned = chapter_title.replace('\\', '').replace('/', '').replace(':', ' -').replace('*', '').replace('?', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '').replace(',', '')
    return chapter_title_cleaned
   
   
# Remove and/or replace unwanted weird symbols that gets scraped    
def remove_weird_symbols(text_paragraph):
    # Remove and/or replace unwanted symbols that gets scraped
    text_paragraph = text_paragraph.replace('  +', '').replace(' +', '').replace('+', '').replace('—', '')
    # Replace the number of comments symbol that gets scraped 
    text_paragraph = re.sub(r"\b[1-9][0-9]?$", '', text_paragraph, flags=re.MULTILINE) 
    # Replace other weird symbols
    text_paragraph = text_paragraph.replace('—', '')
    return text_paragraph
    

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()  
    page = context.new_page()
    
    # Read novels to be scraped from file
    with open('novel_links.txt', 'r', encoding='utf-8') as links_file:
        story_links = links_file.readlines()
        
        for story_link in story_links:
        
            # Open the story's main page
            page.goto(story_link)
            
            # Get story title
            story_title =  page.query_selector(".story-info__title").inner_text().replace("Iseka...", "Isekai'd")
            print(f"{showTime()} {story_title}")
            
            # Get story author
            story_author =  page.query_selector(".author-info__username").inner_text()
            print(f"{showTime()} {story_author}")
 
            # Gradually scroll down to load all content
            press_page_down(page=page, how_many_times=20)
            
            # Query selectors with links for chapters
            chapters = page.query_selector_all('.story-parts >> ul >> li >> a')
                      
            # Prepare empty list to store chapter links
            chapter_links = []
            
            # Concatenate href for the chapter to the main website URL and append created link to the list
            for chapter in chapters:
                chapter_links.append('https://www.wattpad.com' + chapter.get_attribute('href'))
                
            # Loop through each chapter in the gathered list
            i=1
            for chapter_link in chapter_links:

                # Prepare empty variable for paragraph
                text_paragraph = ""
                
                page.goto(chapter_link)
                
                # Gradually scroll down to load all content
                press_page_down(page=page)
                
                # Get title
                chapter_title = page.query_selector(".h2").inner_text()
                #print(chapter_title)
                
                # Remove and/or replace illegal characters for directory name from chapter title
                chapter_title = remove_illegal_symbols(chapter_title)
                #print(chapter_title)
               
                # Paragraph selectors in the pre tags hold the story text, query all of them
                paragraphs = page.query_selector_all('pre p')
                
                # Get text content form paragraph selectors
                for paragraph in paragraphs:
                    text_paragraph += paragraph.text_content()
                    text_paragraph += '\n'
                    #print(text_paragraph)
                #programPause = input("Press the <ENTER> key to continue...")
                
                # Remove and/or replace unwanted weird symbols that gets scraped
                text_paragraph = remove_weird_symbols(text_paragraph)
                
                # Check for redundant 'chapter' word
                if not "Chapter" in chapter_title or "chapter" in chapter_title or "CHAPTER" in chapter_title:
                    # Create chapter info title
                    chapter_info = f"{story_title},\nChapter number {i}: {chapter_title},\nWritten by {story_author}.\n\n\n"
                else:
                    chapter_info = f"{story_title},\n{chapter_title},\nWritten by {story_author}.\n\n\n"
                # Check for redundant 'chapter' word    
                if not "Chapter" in chapter_title or "chapter" in chapter_title or "CHAPTER" in chapter_title:
                    # Create directory name for chapter
                    story_and_chapter = f"{story_title},  Chapter number {i} - {chapter_title}"
                else:
                    story_and_chapter = f"{story_title},  {chapter_title}"
                
                if not os.path.exists(f"chapters/{story_and_chapter}"):
                    os.makedirs(f"chapters/{story_and_chapter}") 
               
                # Write chapters into files in separate directories
                with open(f"chapters/{story_and_chapter}/story.txt", 'w', encoding="utf-8", newline='\n') as file:
                    file.write(chapter_info + text_paragraph + '\n\n\n\n')
                    
                print(f"{showTime()}\n{chapter_info} Done!\n")
                i=i+1

        context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
