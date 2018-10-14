echo start file index:
read start_index
echo end file index:
read end_index
for i in $(seq $start_index $end_index);
do
    echo run main_test.py where index==$i;
    python main_test.py $i;
done
