library(ggplot2)
theme_set(theme_bw())

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

# See https://github.com/Ecotrust/growth-yield-batch/wiki/Prepping-data-for-blm-project#preprocess-using-sql-query
d <- read.csv("../data/graph_scheduled.csv")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))

clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim85 <- noclim
noclim45$rcp <- "rcp45"
noclim85$rcp <- "rcp85"
noclim <- rbind(noclim45, noclim85)

cp <- ggplot(data=clim, aes(x=year, y=carbon)) +
      ggtitle("Total Carbon") +
      facet_grid(. ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=carbon), se=FALSE, span=0.3) +
      ylab("tons") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      theme(axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_rect(fill="white", colour="white"),
            plot.background = element_rect(color="white"),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank(),
            axis.title.x=element_blank())     


vp <- ggplot(data=clim, aes(x=year, y=standing)) +
      ggtitle("Volume of Standing Timber") +
      facet_grid(. ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=standing), se=FALSE, span=0.3) +
      ylab("cubic feet") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      theme(axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            strip.text=element_blank(),
            plot.background = element_rect(color="white"),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank(),
            axis.title.x=element_blank())     


tp <- ggplot(data=clim, aes(x=year, y=timber)) +
      ggtitle("Timber Harvested") +
      facet_grid(. ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=timber), se=FALSE, span=0.3) +
      ylab("boardfeet") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      theme(axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            strip.text=element_blank(),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank(),
            axis.title.x=element_blank())     



fp <- ggplot(data=clim, aes(x=year, y=fire)) +
      ggtitle("Acres of High Fire Risk") +
      facet_grid(. ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=fire), se=FALSE, span=0.3) + 
      ylab("fire rating") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      theme(axis.text.y=element_blank(),
            strip.background=element_blank(),
            strip.text=element_blank(),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank(),
            axis.ticks=element_blank())


multiplot(cp, vp, tp, fp)
