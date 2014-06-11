library(ggplot2)
library(grid)
theme_set(theme_bw())

source("./utils.r")

d <- runsql("select 'rx' || rx as rx, rx as rxnum, climate, count(rx) as rxcount from optimalrx group by rx, climate order by rxnum")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
d$circ = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 1))
d[d$climate == "NoClimate", ]$rcp <- "rcp45"

d$climfact <- factor(d$climate, levels=c(
  "CCSM4-rcp45", 
  "Ensemble-rcp45",  
  "GFDLCM3-rcp45",
  "HadGEM2ES-rcp45", 
  "CCSM4-rcp85",
  "Ensemble-rcp85",
  "GFDLCM3-rcp85",
  "HadGEM2ES-rcp85",
  "NoClimate"
), ordered=TRUE)

d$rxfact <- factor(d$rx, levels=c(
  'rx1',
  'rx9',
  'rx7',
  'rx6',
  'rx5',
  'rx4',
  'rx3',
  'rx8',
  'rx2'
), ordered=TRUE)

pie <- ggplot(d, aes(x="", y=rxcount, fill=rxfact, order=rxfact)) + geom_bar(stat="identity") +
  facet_grid(rcp ~ circ) +
  theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        axis.title.x=element_blank(),
        legend.position="right", # TODO 
        legend.direction="vertical",
        axis.title.y=element_blank()) +
  coord_polar(theta="y") + 
  scale_fill_brewer(palette="YlGn", name="Rx",
                    labels=c(
                      'Grow Only',
                      'Patch cut',
                      'Complex thin',
                      '20 yr thin',
                      '100+ yr',
                      '80 yr',
                      '60 yr',
                      '50 yr',
                      '40 yr'
                    )) 

print(pie)


###################################
# d <- runsql("select 'rx' || rx as rx, rx as rxnum, climate, count(rx) as rxcount from optimalrx group by rx, climate order by rxnum")
# d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
# d$circ = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 1))
# d[d$climate == "NoClimate", ]$rcp <- 0
# d[d$rcp == "rcp45", ]$rcp <- 4.5
# d[d$rcp == "rcp85", ]$rcp <- 8.5

# da <- aggregate(rxcount ~ rcp + rx, data=d, mean)
# write.csv(da, '')