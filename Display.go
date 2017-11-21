package core

import (
	"github.com/fogleman/gg"
	"strconv"
	"math"
)

const (
	DISPLAY_WIDTH = 3600
	DISPLAY_ENABLED = false
)

type SystemDisplay int

const (
	NAV_DISPLAY SystemDisplay = iota
	ORDER_DISPLAY
	COMET_DISPLAY
	KITE_DISPLAY
	MAP_DISPLAY
)

var SystemsEnabled = map[SystemDisplay]bool {
	NAV_DISPLAY: true,
	COMET_DISPLAY: false,
	KITE_DISPLAY: false,
	MAP_DISPLAY: true,
	ORDER_DISPLAY: true,
}

func (game Game) IsDisplayingSystem(sys SystemDisplay) bool {
	return game.display != nil && DISPLAY_ENABLED && SystemsEnabled[sys]
}

func (game Game) ShowMap() {
	if game.display == nil {
		game.LogOnce("Display is nil, not saving images")
		return
	}
	game.LogOnce("Display exists, saving images")

	d := game.display

	for _, planet := range game.AllPlanets() {
		game.Log("Drawing circle for planet %v", planet)
		game.DrawEntity(planet, .9,.9,.9, 0, MAP_DISPLAY)
	}

	for _, ship := range game.AllShips() {
		game.Log("Drawing circle for ship %v", ship)
		game.DrawEntity(ship,0,0,1, .5, MAP_DISPLAY)
		game.DrawString(strconv.Itoa(ship.Id), ship.GetX(), ship.GetY(), 0,0,0,1, MAP_DISPLAY)
	}

	path := "go_bot/thoughts/" + strconv.Itoa(game.pid) + "-" + strconv.Itoa(game.turn) + ".png"
	game.Log("Saving image to path: %v", path)
	d.SavePNG(path)
	d.SetRGB(1,1,1)
	d.Clear()
}

func (game Game) DrawEntity(e Entity, r,g,b, w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		d := game.display

		ratio := Ratio(game)
		d.DrawCircle(e.GetX()*ratio, e.GetY()*ratio, e.GetRadius()*ratio)
		game.SetContextDisplay(r,g,b,w)
	}
}

func (game Game) SetContextDisplay(r,g,b,w float64) {
	d := game.display
	d.SetRGB(r, g, b)
	if w > 0 {
		d.SetLineWidth(w)
		d.Stroke()
	} else {
		d.Fill()
	}
}

func (game Game) DrawLineString(points []Entity, r,g,b,w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		for i, _ := range points {
			if i+1 < len(points) {
				game.DrawLine(points[i], points[i+1], r, g, b, w, sys)
			}
		}
	}
}

func (game Game) DrawPolygon(points []Entity, r,g,b,w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		for i, _ := range points {
			if i+1 == len(points) {
				game.DrawLine(points[i], points[0], r, g, b, w, sys)
			} else {
				game.DrawLine(points[i], points[i+1], r, g, b, w, sys)
			}
		}
	}
}

func (game Game) DrawLine(start, end Entity, r,g,b,w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		d := game.display
		ratio := Ratio(game)
		d.DrawLine(start.GetX()*ratio, start.GetY()*ratio, end.GetX()*ratio, end.GetY()*ratio)
		game.SetContextDisplay(r,g,b,w)
	}
}


func (game Game) DrawString(s string, x, y, r,g,b,w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		d := game.display
		ratio := Ratio(game)
		d.DrawString(s, x*ratio,y*ratio)
		game.SetContextDisplay(r,g,b,w)
	}
}

func (game Game) DrawArc(source, target Entity, radius, lowAngle, highAngle, r,g,b,w float64, sys SystemDisplay) {
	if game.IsDisplayingSystem(sys) {
		d := game.display
		ratio := Ratio(game)


		if math.Abs(lowAngle - highAngle) > 180 {
			if highAngle > lowAngle {
				highAngle -= 360
			} else {
				lowAngle -= 360
			}
		}
		d.DrawArc(source.GetX()*ratio, source.GetY()*ratio, radius*ratio, gg.Radians(lowAngle), gg.Radians(highAngle) )

		game.SetContextDisplay(r,g,b,w)
	}
}

func Ratio(game Game) float64 {
	return float64(DISPLAY_WIDTH)/float64(game.width)
}

func CreateDisplayContext(game Game) *gg.Context {
	w := DISPLAY_WIDTH
	h := int(float64(game.height) * Ratio(game))
	ctx := gg.NewContext(w, h)
	ctx.SetRGB(1,1,1)
	ctx.Clear()
	return ctx
}