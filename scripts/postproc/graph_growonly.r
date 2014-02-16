library(ggplot2)
library(grid)
library(RSQLite)

runsql <- function(sql, dbname="/home/mperry/projects/BLM_climate/Batch1/master.sqlite"){
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

# Data ... unscheduled grow-only
# CREATE TABLE growonly_summary AS
# SELECT year, climate, district,
#        sum(calc_carbon * acres) as carbon, sum(after_total_ft3 * acres) as volume
# FROM fvsaggregate AS fvs
# JOIN stands ON stands.standid = fvs.cond
# WHERE calc_carbon IS NOT NULL
# AND fvs.rx = 1
# GROUP BY year, climate, district

d <- runsql("SELECT * FROM growonly_summary")

d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))

# scale some units
#d$timber <- d$timber/1000
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


formatter <- function(x){ 
    return((20*x)/1000000);
}

clim$carbon_norm <- clim$carbon / noclim$carbon
noclim$carbon_norm <- noclim$carbon / noclim$carbon

cp <- ggplot(data=clim, aes(x=year, y=carbon_norm)) +
  ggtitle("Total Carbon based on 5% subset") +
  facet_grid(district ~ rcp) +
  geom_line(color="grey", alpha=0.5, size=2) +
  # When we get more climate circ models, ...
  # stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
  geom_smooth(data=noclim, aes(x=year, y=carbon_norm), se=FALSE, span=0.3) +
  ylab("Millions of Tons") +
  scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
  scale_y_continuous(labels=formatter) +
  theme(
        #axis.text.x=element_blank(),
        #axis.text.y=element_blank(),
        #axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white")
        #plot.background = element_rect(color="white"),
        #plot.margin = unit(c(0.5,0,0,0), "cm"),
        #panel.border=element_blank()
        #axis.title.x=element_blank()
       )     

print(cp)
#multiplot(cp, vp)
#ggsave(cp, filename="growonly_carbon_bydistrict_sample5pct.pdf", height=11.5, width=8)
#ggsave(vp, filename="growonly_volume_bydistrict_sample5pct.pdf", height=11.5, width=8)
