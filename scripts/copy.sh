# first create files.txt
# ls -1 /mnt/ebsFINAL/ > files.txt
psql -d forestplanner -U ubuntu -c "DELETE FROM trees_fvsaggregate;"
psql -d forestplanner -U ubuntu -c "DELETE FROM trees_conditionvariantlookup;"

while read p; do
  echo $p
  psql -d forestplanner -U ubuntu -c "COPY trees_fvsaggregate(\"agl\",\"bgl\",\"calc_carbon\",\"cond\",
                        \"dead\",\"offset\",\"rx\",\"site\",\"total_stand_carbon\",\"var\",
                        \"year\",\"merch_carbon_removed\",\"merch_carbon_stored\",
                        \"cedr_bf\",\"cedr_hrv\",\"ch_cf\",\"ch_hw\",\"ch_tpa\",
                        \"cut_type\",\"df_bf\",\"df_hrv\",\"es_btl\",\"firehzd\",\"hw_bf\",
                        \"hw_hrv\",\"lg_cf\",\"lg_hw\",\"lg_tpa\",\"lp_btl\",\"mnconbf\",
                        \"mnconhrv\",\"mnhw_bf\",\"mnhw_hrv\",\"nsodis\",\"nsofrg\",
                        \"nsonest\",\"pine_bf\",\"pine_hrv\",\"pp_btl\",\"sm_cf\",\"sm_hw\",
                        \"sm_tpa\",\"spprich\",\"sppsimp\",\"sprc_bf\",\"sprc_hrv\",
                        \"wj_bf\",\"wj_hrv\",\"ww_bf\",\"ww_hrv\",\"after_ba\",
                        \"after_merch_bdft\",\"after_merch_ft3\",\"after_total_ft3\",
                        \"after_tpa\",\"age\",\"removed_merch_bdft\",
                        \"removed_merch_ft3\",\"removed_total_ft3\",\"removed_tpa\",
                        \"start_ba\",\"start_merch_bdft\",\"start_merch_ft3\",
                        \"start_total_ft3\",\"start_tpa\")
                    FROM '/mnt/ebsFINAL/$p'
                    DELIMITER ',' CSV HEADER;"
done < files.txt
