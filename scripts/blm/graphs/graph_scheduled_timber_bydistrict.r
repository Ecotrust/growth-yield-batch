library(ggplot2)
theme_set(theme_bw())

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

# See https://github.com/Ecotrust/growth-yield-batch/wiki/Prepping-data-for-blm-project#preprocess-using-sql-query
d <- runsql("SELECT s.year, s.district, s.climate as climate,
                sum(carbon) as carbon, sum(timber) as timber, 
                sum(standing) as standing, sum(fire) as fire,
                sum(owl) as owl, sum(cost) as cost
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate, s.district;")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))

clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim85 <- noclim
noclim45$rcp <- "rcp45"
noclim85$rcp <- "rcp85"
noclim <- rbind(noclim45, noclim85)


tp <- ggplot(data=clim, aes(x=year, y=timber)) +
      ggtitle("Timber Harvested") +
      facet_grid(district ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=timber), se=FALSE, span=0.3) +
      ylab("boardfeet") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      theme(#axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            #strip.text=element_blank(),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank())
            #axis.title.x=element_blank())     

print(tp)
