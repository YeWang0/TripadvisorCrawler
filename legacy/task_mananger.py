from Shard.TaskSharder import TaskSharder
ts = TaskSharder()
# ts.shard_reviewer(100, '../data/reviewer_split/Tripadvisor_reviewer_path.xlsx')
ts.shard("../data/hotels_by_city/Dallas_filled.xlsx", "../data/hotels_by_city/Dallas/Dallas_shard_{}.xlsx")
