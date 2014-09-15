library(ggplot2)
theme_set(theme_bw())

source("/home/mperry/src/growth-yield-batch/scripts/blm/graphs/utils.r", chdir=T)

# See https://github.com/Ecotrust/growth-yield-batch/wiki/Prepping-data-for-blm-project#preprocess-using-sql-query
d <- read.csv("../data/graph_scheduled_bydistrict.csv")
d$rcp = as.character(lapply(strsplit(as.character(d$climate), split="-"), "[", 2))
lowem <- "RCP 4.5"
highem <- "RCP 8.5"
d[d$rcp == "rcp45" & !is.na(d$rcp),]$rcp <- lowem
d[d$rcp == "rcp85" & !is.na(d$rcp),]$rcp <- highem

d$districtf <- factor(d$district, levels=c('Salem District', 'Eugene District', 'Coos Bay District',
                                           'Medford District', 'Roseburg District', 'Lakeview District'))

d <- subset(d, districtf %in% c('Medford District', 'Roseburg District', 'Lakeview District'))

mult <- 1/0.0477  # 4.77% sample
d$carbon_millionmetrictonnes = mult * d$carbon / 1000000
d$standing_millioncubicft = mult * d$standing / 1000000
d$timber_mmbf = (mult * d$timber / 1000) / 5  # timber is per period, convert to annual
d$fire_thousandacres = mult * d$fire / 1000


cairo_pdf(filename = "/home/mperry/src/growth-yield-batch/scripts/blm/graphs/output/graph_scheduled_bydistrict_South.pdf",
          width = 8.5, height = 11, family = "Georgia")

clim <- subset(d, climate != "NoClimate")
noclim <- subset(d, climate == "NoClimate")

# copy the noclim data with rcps
noclim45 <- noclim
noclim85 <- noclim
noclim45$rcp <- lowem
noclim85$rcp <- highem
noclim <- rbind(noclim45, noclim85)


cp <- ggplot(data=clim, aes(x=year, y=carbon_millionmetrictonnes)) +
      ggtitle("Total Carbon") +
      # facet_grid(districtf ~ rcp) +
      facet_grid(rcp ~ districtf) +
      # facet_wrap(rcp ~ districtf, nrow=1) +
      # facet_wrap(districtf ~ rcp, nrow=1) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=carbon_millionmetrictonnes), se=FALSE, span=0.3) +
      ylab("Million Metric Tonnes") +
      # scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2060, 2100)) +
      theme(#axis.text.x=element_blank(),
            #axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            # strip.text.y=element_blank(),
            # strip.text.x=element_blank(),
            strip.background=element_rect(fill="white", colour="white"),
            plot.background = element_rect(color="white"),
            plot.margin = unit(c(0.5,1.0,0,0), "cm"),
            panel.border=element_blank()
            #axis.title.x=element_blank()
            )     


vp <- ggplot(data=clim, aes(x=year, y=standing_millioncubicft)) +
      ggtitle("Volume of Standing Timber") +
      # facet_grid(districtf ~ rcp) +
      facet_grid(rcp ~ districtf) +
      # facet_wrap(rcp ~ districtf, nrow=1) +
      # facet_wrap(districtf ~ rcp, nrow=1) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=standing_millioncubicft), se=FALSE, span=0.3) +
      ylab("Million Cubic Feet") +
      # scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2060, 2100)) +
      theme(#axis.text.x=element_blank(),
            #axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            strip.text.x=element_blank(),
            strip.text.y=element_blank(),
            plot.background = element_rect(color="white"),
            plot.margin = unit(c(0.5,1.0,0,0), "cm"),
            panel.border=element_blank()
            #axis.title.x=element_blank()
            )     


tp <- ggplot(data=clim, aes(x=year, y=timber_mmbf)) +
      ggtitle("Annual Timber Harvested") +
      # facet_grid(districtf ~ rcp) +
      facet_grid(rcp ~ districtf) +
      # facet_wrap(rcp ~ districtf, nrow=1) +
      # facet_wrap(districtf ~ rcp, nrow=1) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=timber_mmbf), se=FALSE, span=0.3) +
      ylab("Million Boardfeet (mmbf)") +
      #scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2040, 2060, 2080, 2100)) +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2060, 2100)) +
      theme(#axis.text.x=element_blank(),
            #axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            strip.background=element_blank(),
            strip.text.x=element_blank(),
            strip.text.y=element_blank(),
            plot.margin = unit(c(0.5,1.0,0,0), "cm"),
            panel.border=element_blank()
            #axis.title.x=element_blank()
            )     



fp <- ggplot(data=clim, aes(x=year, y=fire_thousandacres)) +
      ggtitle("Area of High Fire Risk") +
      # facet_grid(districtf ~ rcp) +
      facet_grid(rcp ~ districtf) +
      # facet_wrap(rcp ~ districtf, nrow=1) +
      # facet_wrap(districtf ~ rcp, nrow=1) +
      stat_summary(geom="ribbon", fun.ymin="min", fun.ymax="max", alpha=0.25) +
      geom_smooth(data=noclim, aes(x=year, y=fire_thousandacres), se=FALSE, span=0.3) + 
      ylab("Thousand Acres") +
      scale_x_continuous(limits=c(2015, 2108), breaks=c(2020, 2060, 2100)) +
      theme(#axis.text.y=element_blank(),
            strip.background=element_blank(),
            strip.text.x=element_blank(),
            strip.text.y=element_blank(),
            plot.margin = unit(c(0.5,1.0,0,0), "cm"),
            panel.border=element_blank(),
            axis.ticks=element_blank())


multiplot(cp, vp, tp, fp)
