library(ggplot2)
theme_set(theme_bw())

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

# see wiki 
d <- runsql("SELECT year, district, climate, sum(carbon) as carbon
             FROM fvs_stands 
             WHERE rx = 1 
             GROUP BY year, district, climate
             ORDER BY year, district, climate")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))


clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim85 <- noclim
noclim45$rcp <- "rcp45"
noclim85$rcp <- "rcp85"
noclim <- rbind(noclim45, noclim85)


formatter <- function(x){ 
    return((20*x)/1000000);
}

# clim$carbon_norm <- clim$carbon / noclim$carbon
# noclim$carbon_norm <- noclim$carbon / noclim$carbon

cp <- ggplot(data=clim, aes(x=year, y=carbon)) +
  ggtitle("Total Carbon based on 5% subset") +
  facet_grid("rcp ~ district") +
  # geom_line(color="grey", alpha=0.5, size=2) +
  # When we get more climate circ models, ...
  stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
  geom_smooth(data=noclim, aes(x=year, y=carbon), se=FALSE, span=0.3) +
  #ylab("Millions of Tons") +
  scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
  scale_y_continuous(labels=formatter) +
  theme(
        axis.text.x=element_blank(),
        axis.text.y=element_blank(),
        axis.ticks=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank()
        #axis.title.x=element_blank()
       )     

print(cp)
#multiplot(cp, vp)
#ggsave(cp, filename="growonly_carbon_bydistrict_sample5pct.pdf", height=11.5, width=8)
#ggsave(vp, filename="growonly_volume_bydistrict_sample5pct.pdf", height=11.5, width=8)
