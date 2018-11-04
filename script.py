from package.data_crawler.tripadvisor_task_handler import *
from package.utils.utils import get_all_files, get_all_files_recursively
from package.utils.utils import check_hotel_reviews_crawled, check_hotel_reviews_match
from package.utils.utils import create_folder
import signal
from package.timer.timer import signal_handler
import traceback
from shutil import copyfile, move

if __name__ == '__main__':
    cities = ['Dallas', 'Denver', 'Houston', 'Los_Angeles', 'New_Orleans', 'Miami']

    # count files in folder
    # files_recursively = get_all_files_recursively("data/hotel_data/gcp_task/", suffix='.xlsx')
    # print len(files_recursively)
    # exit(0)

    task_id = 1
    if task_id == 0:
        # find defective crawled file
        data_folder = "data/hotels_by_city/{}/"
        sum_reviews = 0
        review_mod = 2000
        for city in cities:
            print city
            files_recursively = get_all_files(data_folder.format(city), suffix='.xlsx')

            for hotel_file in files_recursively[:]:
                matched, english_review_num, crawled_reviews_count = check_hotel_reviews_match(hotel_file, 0.9)
                if not matched:
                    print hotel_file, '\n', english_review_num, crawled_reviews_count
                # break
                    if english_review_num == -1:
                        # move to passed case
                        create_folder('data/hotel_data/gcp_task/{}/'.format('passed'))
                        # break
                        print "Move from {} to {}".format(hotel_file, 'data/hotel_data/gcp_task/{}/'.format('passed') +
                                                          hotel_file.split('/')[-1])
                        copyfile(hotel_file, 'data/hotel_data/gcp_task/{}/'.format('passed') + hotel_file.split('/')[-1])
                    else:
                        hotel_info = read_xls(hotel_file, ['hotel_info'])['hotel_info']
                        num_index = hotel_info[0].index('Total_Reviews_num')
                        num_reviews = 1
                        try:
                            if len(hotel_info) > 1 and num_index > 0 and num_index < len(hotel_info[1]):
                                num_reviews = int(hotel_info[1][num_index])
                        except Exception as e:
                            print e
                        sum_reviews += num_reviews
                        index = sum_reviews // review_mod
                        create_folder('data/hotel_data/gcp_task/{}/'.format(index))
                        # break
                        print "Move from {} to {}".format(hotel_file, 'data/hotel_data/gcp_task/{}/'.format(index) + hotel_file.split('/')[-1])
                        copyfile(hotel_file, 'data/hotel_data/gcp_task/{}/'.format(index) + hotel_file.split('/')[-1])

    elif task_id == 1:
        # move gcp crawled data to local folder
        gcp_folder = 'data/todo/{}'
        data_folder = "data/hotels_by_city/{}/"
        for i in xrange(1):
            files_recursively = get_all_files(gcp_folder.format(i), suffix='.xlsx')
            for city in cities:
                print city
                for hotel_file in files_recursively:
                    if city.lower() in hotel_file.lower():
                        # print city, hotel_file
                    # else:
                    #     print hotel_file
                        if check_hotel_reviews_crawled(hotel_file):
                            print "Move from {} to {}".format(hotel_file, data_folder.format(city) + hotel_file.split('/')[-1])
                            move(hotel_file, data_folder.format(city) + hotel_file.split('/')[-1])
                # print data_folder.format(city)

    elif task_id == 2:
        # find out un-crawled tasks
        sum_reviews = 0
        count = 0
        review_mod = 10000
        while True:
            # city = cities[4]
            data_folder = "data/hotels_by_city/" #+ city
            output_folder = "data/gcp-11-1/{}/"
            output_root = "data/gcp-11-1/"
            create_folder(output_root)
            files = get_all_files(data_folder, suffix='.xlsx')
            files_recursively = get_all_files_recursively(data_folder, suffix='.xlsx')
            print len(files)
            print len(files_recursively)

            for f in files_recursively[:]:
                # this file is not crawled yet
                if not check_hotel_reviews_crawled(f):
                    # print read_xls(f)
                    # print '===get_hotel_tripadvisor_reviews : {}'.format(f)
                    # # set timeout for single crawling task
                    # signal.signal(signal.SIGALRM, signal_handler)
                    # signal.alarm(crawler_timeout)
                    # try:
                    #     get_hotel_tripadvisor_reviews(f)
                    # except Exception as e:
                    #     print e
                    hotel_info = read_xls(f, ['hotel_info'])['hotel_info']
                    num_index = hotel_info[0].index('Total_Reviews_num')
                    num_reviews = 1
                    try:
                        if len(hotel_info) > 1 and num_index > 0 and num_index < len(hotel_info[1]):
                            num_reviews = int(hotel_info[1][num_index])
                    except Exception as e:
                        traceback.print_exc()
                        # break
                    sum_reviews += num_reviews
                    index = sum_reviews // review_mod
                    create_folder(output_folder.format(index))
                    # break
                    print "Move from {} to {}".format(f, output_folder.format(index) + f.split('/')[-1])
                    copyfile(f, output_folder.format(index) + f.split('/')[-1])
                    count += 1
                    print "Total unfinished task: {}".format(count)
            break
