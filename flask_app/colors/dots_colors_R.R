require(RColorBrewer)

color_blue <- rgb(maxColorValue = 255, 0, 51, 102)
color_gold <- rgb(maxColorValue = 255, 255, 204, 0)

colors_dots <- c(rgb(maxColorValue = 255, 66, 179, 76), #Groen
                  rgb(maxColorValue = 255, 34, 179, 200), # Blauw
                  rgb(maxColorValue = 255, 247, 79, 69), # Rood
                  rgb(maxColorValue = 255, 252, 182, 67), # Geel
                  rgb(maxColorValue = 255, 146, 80, 122), # Paars
                  rgb(maxColorValue = 255, 236, 226, 214)) # Grijs

plot(x = seq(1:6), y = seq(1:6),
     col = colors_dots, pch=19, cex = 10)

# Wedding invitation colors
color_blue <- rgb(maxColorValue = 255, 0, 51, 102)
color_gold <- rgb(maxColorValue = 255, 255, 204, 0)
ramp <- colorRamp(colors = c(color_blue, color_gold ))
colors <- rgb( ramp(seq(0, 1, length = 10)), max = 255)
#colors <- colors[-1]
#colors <- colors[-length(colors)]
plot(x = seq(1:length(colors)), y = seq(1:length(colors)),
     col = colors, pch=19, cex = 10)

# Blue range for font
color_blue <- rgb(maxColorValue = 255, 0, 51, 102)
color_gold <- rgb(maxColorValue = 255, 255, 204, 0)
ramp <- colorRamp(colors = c(color_blue, 'white' ))
colors <- rgb( ramp(seq(0, 1, length = 10)), max = 255)
plot(x = seq(1:length(colors)), y = seq(1:length(colors)),
     col = colors, pch=19, cex = 10)

# Yellow range for background
yellow <- rgb(maxColorValue = 255, 252, 182, 67) # Geel
ramp <- colorRamp(colors = c(yellow, 'white' ))
colors <- rgb( ramp(seq(0, 1, length = 10)), max = 255)
plot(x = seq(1:length(colors)), y = seq(1:length(colors)),
     col = colors, pch=19, cex = 10)
