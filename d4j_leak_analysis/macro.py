from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time, json

def init():
    browser = webdriver.Chrome()
    browser.get("https://stack.dataportraits.org")
    time.sleep(2)
    return browser

def read_buggy_info():
    with open("d4j_data/buggy_snippets.json") as f:
        method_snippets = json.load(f)
    with open("d4j_data/test_snippets.json") as f:
        test_snippets = json.load(f)
    return method_snippets, test_snippets

def insert_string(browser, target_string):
    browser.execute_script(f"document.getElementById(\"query-box\").value=`{target_string}`;")
    input_box = browser.find_element(By.ID, "query-box")
    input_box.send_keys(" \b")
    time.sleep(2)

def get_longest_match(browser):
    try:
        longest_matches = browser.find_element(By.ID, "card-results")
        longest_match = len(longest_matches.find_elements(By.CLASS_NAME, "card-body")[0].get_attribute("innerHTML"))
    except Exception:
        longest_match = 0
    return longest_match

def get_overall_match(browser):
    try:
        matching_text_box = browser.find_element(By.ID, "echo")
    except Exception:
        return 0
    all_characters = matching_text_box.find_elements(By.CSS_SELECTOR, "span")
    data_portrait_len = len(all_characters)
    overall_match_count = len([e for e in all_characters if "highlight-" in e.get_attribute("class")])
    return data_portrait_len, overall_match_count

def main(browser, prior_data=None):
    method_snippets, test_snippets = read_buggy_info()
    if prior_data is None:
        overlap_info = []
        done_bugs = set()
    else:
        overlap_info = prior_data
        done_bugs = set([e["bug_name"] for e in overlap_info])
        
    for bug_name in test_snippets:
        if bug_name in done_bugs:
            continue
        max_test_proportion = -1
        max_test_long_match = -1
        max_test_len = -1
        selected_test_raw_len = -1
        for test_snip in test_snippets[bug_name]:
            test_raw_len = len(test_snip)
            test_snip = test_snip[:2000] # data portrait can't handle inputs too long
            insert_string(browser, test_snip)
            test_longest_match_len = get_longest_match(browser)
            test_len, test_overall_match_len = get_overall_match(browser)
            test_overall_proportion = test_overall_match_len / test_len
            if max_test_proportion < test_overall_proportion:
                max_test_proportion = test_overall_proportion
                max_test_long_match = test_longest_match_len
                max_test_len = test_len
                selected_test_raw_len = test_raw_len
        
        max_code_proportion = -1
        max_code_long_match = -1
        max_code_len = -1
        selected_code_raw_len = -1
        for method_snip in method_snippets[bug_name]:
            code_raw_len = len(method_snip)
            method_snip = method_snip[:2000] # ditto above
            insert_string(browser, method_snip)
            code_longest_match_len = get_longest_match(browser)
            code_len, code_overall_match_len = get_overall_match(browser)
            code_overall_proportion = code_overall_match_len / code_len
            if max_code_proportion < code_overall_proportion:
                max_code_proportion = code_overall_proportion
                max_code_long_match = code_longest_match_len
                max_code_len = code_len
                selected_code_raw_len = code_raw_len
        
        overlap_info.append({
            'bug_name': bug_name,
            'max_test_proportion': max_test_proportion,
            'max_test_long_match': max_test_long_match,
            'max_test_len': max_test_len,
            'sel_test_raw_len': selected_test_raw_len,
            'max_code_proportion': max_code_proportion,
            'max_code_long_match': max_code_long_match,
            'max_code_len': max_code_len,
            'sel_code_raw_len': selected_code_raw_len,
        })
        with open("results/overlap_data.json", "w") as f:
            json.dump(overlap_info, f)

if __name__ == "__main__":
    browser = init()
    main(browser)