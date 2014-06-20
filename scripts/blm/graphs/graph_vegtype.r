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

# forest types with present day > 1% 
# d$fortypefact <- addNA(factor(d$fortype, levels=c(
# 	912,
# 	267,
# 	301,
# 	932,
# 	183,
# 	941,
# 	221,
# 	911,
# 	923,
# 	999,
# 	951,
# 	201
# 	), ordered=TRUE))
d$fortypefact <- factor(d$fortype, ordered=TRUE)

print(d$fortypefact)



lines <- ggplot(d, aes(x=year, y=acres, group=fortypefact, order=fortypefact, fill=fortypefact)) + 
    facet_grid(rcp ~ circ) + 
    geom_bar(stat="identity", position="stack", width=5) +
    ggtitle("Future Forest Types, scheduled") +
    #geom_text(stat="identity", position="stack", aes(label=fortype), vjust=0) +
    theme(
        axis.text.y=element_blank(),
        axis.ticks.y=element_blank(),
        strip.background=element_rect(fill="white", colour="white"),
        plot.background = element_rect(color="white"),
        plot.margin = unit(c(0.5,0,0,0), "cm"),
        panel.border=element_blank(),
        #axis.title.x=element_blank(),
        legend.position="bottom", # TODO 
        legend.direction="horizontal",
        legend.box="vertical",
        legend.title=element_text("Forest Type"),  # See page 236 in Essential FVS
        legend.key.size=unit(c(0.5,0.5,0.5,0.5), "cm"),
        axis.title.y=element_blank()) +
    #scale_fill_brewer(palette="Paired", name="Fortype")
    scale_fill_manual(breaks = levels(factor(d$fortypefact)), values = rainbow(42))
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


