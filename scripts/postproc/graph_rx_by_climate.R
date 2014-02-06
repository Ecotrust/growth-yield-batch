library(ggplot2)
library('Cairo')
library(grid)
library(RSQLite)

runsql <- function(sql, dbname="E:/workspace/gnn_build/master.sqlite"){
#runsql <- function(sql, dbname="E:/workspace/gnn_build/try1.db"){
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


d <- runsql( 
    "SELECT fvs.year as year, fvs.climate as climate, 
            sum(calc_carbon) as carbon, sum(after_total_ft3) as volume,
            sum(removed_merch_bdft) as timber, avg(FIREHZD) as fire,
            avg(NSONEST) as owl
            -- todo sum(NSONEST + acres)
    FROM fvsaggregate AS fvs
    JOIN optimalrx AS opt
    ON fvs.cond = opt.stand
    -- todo join with stands to get acres
    WHERE calc_carbon IS NOT NULL
    AND opt.rx = fvs.rx
    AND opt.offset = fvs.offset
    GROUP BY fvs.year, fvs.climate")

# write.csv(d, 'output2.csv')

# d <- read.csv('output2.csv')
d <- runsql("select 'rx' || rx as rx, rx as rxnum, climate, count(rx) as rxcount from optimalrx group by rx, climate order by rxnum")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
d$circ = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 1))

d[d$climate == "NoClimate", ]$rcp <- "rcp45"

d$climfact <- factor(d$climate, levels=c(
    "CCSM4-rcp45", 
    "Ensemble-rcp45",  
    "GFDLCM3-rcp45",
    "HadGEM2ES-rcp45", 

    "CCSM4-rcp60",     
    "Ensemble-rcp60", 
    "GFDLCM3-rcp60",
    "HadGEM2ES-rcp60",

    "CCSM4-rcp85",
    "Ensemble-rcp85",
    "GFDLCM3-rcp85",
    "HadGEM2ES-rcp85",

    "NoClimate"
    ), ordered=TRUE)

d$rxfact <- factor(d$rx, levels=c(
    "rx3",  
    "rx8",
    "rx13", 
    "rx20",     
    "rx25", 
    "rx1"
    ), ordered=TRUE)

bar <- ggplot(d, aes(x=rx, y=rxcount, fill=rx)) + geom_bar(stat="identity") +
      facet_grid(circ ~ rcp) +
      theme(axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        legend.position="none", # TODO 
        axis.title.x=element_blank()) +
       scale_fill_brewer(palette="Spectral")

stacked <- ggplot(d, aes(x=climfact, y=rxcount, fill=rx)) + geom_bar(stat="identity") +
      theme(axis.text.x=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        legend.position="none", # TODO 
        axis.title.x=element_blank()) +
       scale_fill_brewer(palette="Spectral") +
        coord_flip()

      #scale_fill_manual(values=c("blue", "cyan4"))
      #facet_grid(. ~ climate)

pie <- ggplot(d, aes(x="", y=rxcount, fill=rxfact)) + geom_bar(stat="identity") +
      facet_grid(circ ~ rcp) +
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
                          "40 year", 
                          "60 year",
                          "60 year w/ PCT", 
                          "75 year", 
                          "20 year thin", 
                          "Grow only"
                          )) 

# multiplot(bar, stacked, pie, cols=3)
print(pie)
