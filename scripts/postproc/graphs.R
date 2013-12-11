library(ggplot2)
library('Cairo')
library(grid)
library(RSQLite)

#runsql <- function(sql, dbname="E:/workspace/gnn_build/master.sqlite"){
runsql <- function(sql, dbname="E:/workspace/gnn_build/try1.db"){
  require(RSQLite)
  driver <- dbDriver("SQLite")
  connect <- dbConnect(driver, dbname=dbname);
  closeup <- function(){
    sqliteCloseConnection(connect)
    sqliteCloseDriver(driver)
  }
  dd <- tryCatch(dbGetQuery(connect, sql), finally=closeup)
  return(dd)
}

multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  require(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                    ncol = cols, nrow = ceiling(numPlots/cols))
  }

 if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))

      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

theme_set(theme_bw())
# CairoWin()


# d <- runsql( 
    # "SELECT fvs.year as year, fvs.climate as climate, 
    #         sum(calc_carbon) as carbon, sum(after_total_ft3) as volume,
    #         sum(removed_merch_bdft) as timber, avg(FIREHZD) as fire,
    #         avg(NSONEST) as owl
    #         -- todo sum(NSONEST + acres)
    # FROM fvsaggregate AS fvs
    # JOIN optimalrx AS opt
    # ON fvs.cond = opt.stand
    # -- todo join with stands to get acres
    # WHERE calc_carbon IS NOT NULL
    # AND opt.rx = fvs.rx
    # AND opt.offset = fvs.offset
    # GROUP BY fvs.year, fvs.climate")

# write.csv(d, 'output2.csv')

#d <- read.csv('output2.csv')
d <- runsql("select * from try1")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))

# scale some units
d$timber <- d$timber/1000
d$volume <- d$volume/1000

clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim60 <- noclim
noclim85 <- noclim
noclim45$rcp <- "rcp45"
noclim60$rcp <- "rcp60"
noclim85$rcp <- "rcp85"
noclim <- rbind(noclim45, noclim60, noclim85)

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


vp <- ggplot(data=clim, aes(x=year, y=volume)) +
      ggtitle("Volume of Standing Timber") +
      facet_grid(. ~ rcp) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=volume), se=FALSE, span=0.3) +
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
      ggtitle("Average Fire Risk") +
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
