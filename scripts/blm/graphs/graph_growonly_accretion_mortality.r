library(ggplot2)
theme_set(theme_bw())

#########################
#side <- "North"
side <- "South"
#########################

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

# See https://github.com/Ecotrust/growth-yield-batch/wiki/Prepping-data-for-blm-project#preprocess-using-sql-query
d <- read.csv("../data/growonly_vols_district_year_rcp.csv")

d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
d$mort <- -1 * d$mortality_vol / (d$acres * 5) # 5 year period > annual
d$acc <- d$accretion_vol / (d$acres * 5)  # 5 year period > annual

d$districtf <- factor(d$district, levels=c('Salem District', 'Eugene District', 'Coos Bay District',
                                           'Medford District', 'Roseburg District', 'Lakeview District'))

if (side == 'North') {
    d <- subset(d, districtf %in% c('Salem District', 'Eugene District', 'Coos Bay District'))
} else {
    d <- subset(d, districtf %in% c('Medford District', 'Roseburg District', 'Lakeview District'))
}


clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim85 <- noclim
noclim45$rcp <- "rcp45"
noclim85$rcp <- "rcp85"
noclim <- rbind(noclim45, noclim85)

outdir <- "/home/mperry/src/growth-yield-batch/scripts/blm/graphs/output/"
outpath <- paste(outdir, "graph_growonly_accretion_mortality_", side, ".pdf", sep="")

cairo_pdf(filename = outpath, width = 11, height = 8.5, family = "Georgia")

# start_vol,accretion_vol,mortality_vol,removed_vol,year,climate,acres,district



acc <- ggplot(data=clim, aes(x=year, y=acc)) +
      ggtitle("Annual Accretion Rate") +
      #facet_grid(district ~ rcp) +
      facet_grid(rcp ~ districtf) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      # stat_summary(aes(x=year, y=mort), geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=acc), se=FALSE, span=0.3) +
      ylab("Cubic feet per acre") +
      scale_x_continuous(limits=c(2013, 2108), breaks=c(2020, 2060, 2100)) +
      scale_y_continuous(limits=c(0, 320), breaks=c(50, 85, 120, 165, 225)) +
      theme(#axis.text.x=element_blank(),
            #axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            #strip.text=element_blank(),
            #plot.margin = unit(c(1.5,0,0,0), "cm"),
            panel.border=element_blank())
            #axis.title.x=element_blank())    

mort <- ggplot(data=clim, aes(x=year, y=mort)) +
      ggtitle("Annual Mortality Rate") +
      #facet_grid(district ~ rcp) +
      facet_grid(rcp ~ districtf) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      #stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=mort), se=FALSE, span=0.3) +
      ylab("Cubic feet per acre") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2060, 2100)) +
      theme(#axis.text.x=element_blank(),
            #axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            #strip.text=element_blank(),
            plot.margin = unit(c(0.5,0,0,0), "cm"),
            panel.border=element_blank())
            #axis.title.x=element_blank())    


multiplot(acc, mort)
