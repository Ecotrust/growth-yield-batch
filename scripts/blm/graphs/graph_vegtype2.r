library(ggplot2)
theme_set(theme_bw())

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

d <- runsql("
	SELECT s.year as year, s.climate as climate, s.fortype as fortype, sum(s.acres) as acres
    FROM fvs_stands as s
    JOIN optimalrx as o
    ON s.standid = o.stand
    AND s.rx = o.rx
    AND s.offset = o.offset
    AND s.climate = o.climate
    GROUP BY s.year, s.climate, s.fortype;")

# TODO, aggregate into more general forest types

d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
d$circ = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 1))
d[d$climate == "NoClimate", ]$rcp <- "rcp45"

#d <- subset(d, year == 2108)
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

d$fortypefact <- factor(d$fortype, ordered=TRUE)




lines <- ggplot(d, aes(x=year, y=acres, group=climate)) + 
    facet_wrap(~ fortypefact) + 
    geom_line() +
    ggtitle("Future Forest Types, scheduled") +
    theme(
        axis.text.y=element_blank(),
        axis.ticks.y=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        #axis.title.x=element_blank(),
        legend.position="right",
        legend.title=element_text("Forest Type"),  # See page 236 in Essential FVS
        legend.key.size=unit(c(0.5,0.5,0.5,0.5), "cm"),
        axis.title.y=element_blank()) 
    #scale_fill_brewer(palette="Paired", name="Fortype")
    #scale_fill_manual(breaks = levels(factor(d$fortypefact)), values = rainbow(42))
                #     labels=c(
                #     	"bigleaf maple",
          						# "grand fir",
          						# "western hemlock",
          						# "canyon live oak",
          						# "western juniper",
          						# "tanoak",
          						# "ponderosa pine",
          						# "red alder",
          						# "oregon white oak",
          						# "not stocked",
          						# "madrone",
          						# "douglas-fir"
                #     )
                #   ) 
print(lines)
# pie <- ggplot(d, aes(x="", y=acres, fill=fortypefact, order=fortypefact)) + geom_bar(stat="identity") +
#   facet_grid(rcp ~ circ) +
#   theme(axis.text.x=element_blank(),
#         axis.text.y=element_blank(),
#         axis.ticks=element_blank(),
#         strip.background=element_rect(fill="white", colour="white"),
#         plot.background = element_rect(color="white"),
#         plot.margin = unit(c(0.5,0,0,0), "cm"),
#         panel.border=element_blank(),
#         axis.title.x=element_blank(),
#         legend.position="right", # TODO 
#         legend.direction="vertical",
#         axis.title.y=element_blank()) +
  #coord_polar(theta="y") + 


