from ..xlsx_handler.xlsx_handler import read_xls, write_xls


def get_content_rows(file_path, sheet_name):
    try:
        content = read_xls(file_path=file_path, sheet_name_list=[sheet_name])
        # print file_path, sheet_name, len(content[sheet_name])
        if sheet_name in content:
            return len(content[sheet_name])
        else:
            return -1
    except Exception as e:
        print e
        return -1


def check_hotel_reviews_crawled(file_path):
    # review_info, hotel_info
    return get_content_rows(file_path, 'review_info') > 1


def check_hotel_reviews_match(file_path, threshold = 1):
    try:
        content = read_xls(file_path=file_path, sheet_name_list=['hotel_info'])['hotel_info']
        # print content
        head = content[0]
        hotel_info = content[1]
        english_review_num = int(hotel_info[head.index('English_Reviews_num')])
        total_review_num = hotel_info[head.index('Total_Reviews_num')]
        # reviews_count = 0
        crawled_reviews_count = get_content_rows(file_path, 'review_info')
        return crawled_reviews_count/(english_review_num + 0.) >= threshold, english_review_num, crawled_reviews_count
        # return (english_review_num, crawled_reviews_count, english_review_num/crawled_reviews_count)
    except:
        return False, -1, -1


def get_all_files(folder_path, suffix=None):
    from os import listdir
    from os.path import isfile, join
    matched_files = [join(folder_path, f) for f in listdir(folder_path) if isfile(join(folder_path, f)) and (not suffix or f.endswith(suffix))]
    return matched_files


def get_all_files_recursively(folder_path, suffix=None):
    from os import listdir
    from os.path import isfile, isdir, join
    matched_files = [join(folder_path, f) for f in listdir(folder_path)
                     if isfile(join(folder_path, f)) and (not suffix or f.endswith(suffix))]
    sub_folders = [join(folder_path, f) for f in listdir(folder_path) if isdir(join(folder_path, f))]
    for sub_folder in sub_folders:
        matched_files = get_all_files_recursively(sub_folder, suffix) + matched_files
    return matched_files


def create_folder(directory):
    import os
    if not os.path.exists(directory):
        os.makedirs(directory)

# def combine_csv_files(directory):
#     import