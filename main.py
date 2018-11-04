from package.data_crawler.tripadvisor_task_handler import *
from package.utils.utils import get_all_files, get_all_files_recursively
from package.utils.utils import check_hotel_reviews_crawled
from package.utils.utils import create_folder
import signal
from package.timer.timer import signal_handler
from shutil import copyfile, move


task_id_list = ['0']
crawler_timeout = 10000  # hours

if __name__ == '__main__':
    for task_id in task_id_list:
        try:
            data_folder = "data/todo/{}/".format(task_id)

            files = get_all_files(data_folder, suffix='.xlsx')
            files_recursively = get_all_files_recursively(data_folder, suffix='.xlsx')

            print 'Total tasks: ', len(files_recursively)
            done = False
            while not done:
                done = True
                for f in files[:]:
                    # this file is not crawled yet
                    if not check_hotel_reviews_crawled(f):
                        # print read_xls(f)
                        print '===get_hotel_tripadvisor_reviews : {}'.format(f)
                        # set timeout for single crawling task
                        signal.signal(signal.SIGALRM, signal_handler)
                        signal.alarm(crawler_timeout)
                        try:
                            done = get_hotel_tripadvisor_reviews(f)
                            print done
                            if not done:
                                move(f, f.replace('/0/todo', 'failed'))
                        except Exception as e:
                            move(f, f.replace('/0/todo', 'failed'))
                            print e
                        # done = False
        except Exception as e:
            print e


    # print '===get_hotel_tripadvisor_link'
    # get_hotel_tripadvisor_link(path)

    # print '===get_hotel_tripadvisor_summary'
    # get_hotel_tripadvisor_summary(path)

    # print '===get_hotel_tripadvisor_reviews'
    # get_hotel_tripadvisor_reviews(path)

    # print '===update_hotel_reviewer_name'
    # crawl_hotel_reviewer_name(path, reviewer_path)

    # print '===update_hotel_reviewer'
    # update_hotel_reviewer(path, reviewer_path)

    # print '===update_hotel_reviewer_score'
    # update_hotel_reviewer_score(path)

    # print '===update_hotel_review_name'
    # update_hotel_reviewer_name(path)

