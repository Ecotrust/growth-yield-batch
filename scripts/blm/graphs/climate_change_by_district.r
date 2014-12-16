library(ggplot2)

d <- read.csv("/usr/local/apps/growth-yield-batch/scripts/blm/data/climate_change_by_district.csv")
head(d)

cp <- ggplot(data=d, aes(x=Year, y=MeanTemp)) +
  ggtitle("Mean Temp by District") +
  facet_grid(District ~ Scenario) +
  geom_line()

print(cp)
