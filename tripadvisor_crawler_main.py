from tripadvisor_task_handler import *

if __name__ == '__main__':
    import timeit
    # path_template = 'data/split/Tripadvisor_new_orleans_shard_{}.xlsx'
    path_template = "data/hotels_by_city/Dallas/Dallas_shard_{}.xlsx"
    reviewer_path = 'data/Tripadvisor_reviewer_path_ONLY.xlsx'
    # for i in xrange(982, 2000):
    #     reviewer_path = 'data/reviewer_split/Tripadvisor_reviewer_path_shard_{}.xlsx'
    #     print reviewer_path.format(i)
    #     update_hotel_missed_reviewer(reviewer_path.format(i))

    for i in xrange(1, 1000):

        start = timeit.default_timer()
        path = path_template.format(i)
        print "Start to crawl {} at {}...".format(path, start)
        # if getsize(path) > 7000:
        #     print getsize(path)
        #     print 'File already crawled, pass it...'
        #     continue
        # print '===get_hotel_tripadvisor_link'
        # get_hotel_tripadvisor_link(path)
        #
        # print '===get_hotel_tripadvisor_summary'
        # get_hotel_tripadvisor_summary(path)
        #
        # print '===get_hotel_tripadvisor_reviews'
        # get_hotel_tripadvisor_reviews(path)

        print '===update_hotel_reviewer_name'
        crawl_hotel_reviewer_name(path, reviewer_path)

        # print '===update_hotel_reviewer'
        # update_hotel_reviewer(path, reviewer_path)

        # print '===update_hotel_reviewer_score'
        # update_hotel_reviewer_score(path)

        # print '===update_hotel_review_name'
        # update_hotel_reviewer_name(path)
    # #
        stop = timeit.default_timer()

        print stop - start
        # break

# Tripadvisor_Hotel_Name
# Reviews_num
# HotelURL


