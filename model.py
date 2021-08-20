# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 22:05:05 2020

@author: Ricardo
"""
import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import random

import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es

class Person:
    def __init__(self, name = "person", infected = False, nightClub = (0,0)):
        limit = 0.49
        visualLimit = limit + 0.01
        (r,g,b) = (0,0,1)
        if infected:
            (r,g,b) = (1,0,0)
        age = np.random.randint(85)
        family = np.random.randint(9)

        if 0 <= family <= 2:
            (xHouse,yHouse) = (-0.7 + 0.7*family, 0.7)
        elif 3 <= family <= 5:
            (xHouse,yHouse) = (-0.7 + 0.7*(family-3), 0)
        else:
            (xHouse,yHouse) = (-0.7 + 0.7*(family-6), -0.7)
            

        x = np.random.uniform(-limit, limit)
        y = np.random.uniform(-limit, limit)
        gpuColorQuad = es.toGPUShape(bs.createColorQuad(r,g,b))

        person = sg.SceneGraphNode(name)
        person.transform = tr.matmul([tr.translate(x,y,0),tr.uniformScale(0.05)])
        person.childs += [gpuColorQuad]

        self.model = person
        self.name = name
        self.infected = infected
        self.limit = limit
        self.visualLimit = visualLimit
        self.x = x
        self.y = y
        self.xTrip = 0
        self.yTrip = 0
        self.dx = 0.005
        self.dy = 0.005
        self.sign = 0.01
        self.initialDay = 0
        self.day = 0 
        self.tolerance = 0.01
        self.age = age
        self.house = (xHouse, yHouse)
        self.nightClub = nightClub


        

    def draw(self,pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, "transform")
    

    def randomMovement(self):
        if np.random.uniform(0,1)< self.sign:
            self.dx = -self.dx

        if np.random.uniform(0,1)< self.sign:
            self.dy = -self.dy

        if -self.visualLimit < self.x < self.visualLimit:
            self.x += self.dx
            self.model.transform = tr.translate2(self.model.transform, self.dx,0,0)
        else:
            if self.x > 0:
                t = self.limit - self.x 
                self.x = self.limit
                
            else:
                t = -self.limit - self.x
                self.x = -self.limit
            
            self.dx = - self.dx
            self.model.transform = tr.translate2(self.model.transform, t, 0, 0)
        
        if -self.visualLimit < self.y < self.visualLimit:
            self.y += self.dy
            self.model.transform = tr.translate2(self.model.transform, 0, self.dy, 0)
        else:
            if self.y >0:
                t = self.limit - self.y
                self.y = self.limit
            
            else:
                t = -self.limit - self.y
                self.y = -self.limit
            self.dy = -self.dy
            self.model.transform = tr.translate2(self.model.transform, 0, t, 0)

    def update(self,time):
        self.day = time - self.initialDay


    def moveToX(self,x):
        if (self.x > x and self.dx > 0) or (self.x < x and self.dx < 0):
            self.dx = - self.dx
        if not (x - self.tolerance < self.x < x + self.tolerance):
            self.x += self.dx
            self.model.transform = tr.matmul([tr.translate(self.x, self.y, 0), tr.uniformScale(0.05)])

    def moveToY(self,y):
        if (self.y > y and self.dy > 0) or (self.y < y and self.dy < 0):
            self.dy = - self.dy
        if not (y - self.tolerance < self.y < y + self.tolerance):
            self.y += self.dy
            self.model.transform = tr.matmul([tr.translate(self.x,self.y, 0), tr.uniformScale(0.05)])

    def moveToOrigin(self):
        self.moveToX(0)
        self.moveToY(0)

    def party(self):
        if 15 <= self.age <= 40:
            self.moveTo(self.nightClub[0], self.nightClub[1])

    def moveTo(self, x, y):
        self.moveToX(x)
        self.moveToY(y)

    def goHouse(self):
        self.moveTo(self.house[0], self.house[1])
 
        


class Community:
    def __init__(self,pupulation, ratio, countagiusPbb, deathPbb, daysToHeal, x, y, eventPbb,s=1, healPbb = 0.1):
    
        gpuGrayQuad = es.toGPUShape(bs.createColorQuad(0.1,0.1,0.1))
        sickPerson = Person('person' + str(pupulation - 1), True)
        healthPeople = []
        deathPeople = []
        healedPeople = []
        sickPeople = [sickPerson]

        club = (np.random.uniform(-0.49,0.49),np.random.uniform(-0.49,0.49))

        background = sg.SceneGraphNode('background')
        background.transform = tr.uniformScale(1.1)
        background.childs += [gpuGrayQuad]

        community = sg.SceneGraphNode('community')
        community.transform = tr.matmul([tr.uniformScale(s),tr.translate(x,y,0)])
        community.childs += [background, sickPerson.model]
        gpuBlueQuad = es.toGPUShape(bs.createColorQuad(0,0,1))
        gpuRedQuad = es.toGPUShape(bs.createColorQuad(1,0,0))
        gpuYellowQuad = es.toGPUShape(bs.createColorQuad(1,1,0))
        gpuGreenQuad = es.toGPUShape(bs.createColorQuad(0,1,0))
        
        for i in range(pupulation - 1):
            person = Person('person'+str(i), nightClub = club)
            community.childs += [person.model]
            healthPeople.append(person)
            
        self.model = community
        self.healthPeople = healthPeople
        self.sickPeople = sickPeople
        self.deathPeople = deathPeople
        self.healedPeople = healedPeople
        self.ratio = ratio
        self.distance = 1
        self.gpuBlueQuad = gpuBlueQuad
        self.gpuRedQuad = gpuRedQuad
        self.gpuYellowQuad = gpuYellowQuad
        self.gpuGreenQuad = gpuGreenQuad
        self.color = 0
        self.people = self.sickPeople + self.healthPeople 
        self.countagiusPbb = countagiusPbb
        self.deathPbb = deathPbb
        self.daysToHeal = daysToHeal
        self.cardinality = pupulation
        self.x = x
        self.y = y
        self.isParty = False
        self.isQuarantine = False
        self.eventPbb = eventPbb
        self.healPbb = healPbb



    def draw(self,pipeline):
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def personalDistance(self, person1, person2):
        distance = np.sqrt((person2.x - person1.x)**2 + (person2.y - person1.y)**2)
        
        if distance > self.ratio:
            return True
        else:
            return False

    def spread(self, time):
        for i in self.sickPeople:
            if np.random.uniform(0,1) < self.deathPbb:
                    self.sickPeople.remove(i)
                    self.people.remove(i)
                    self.deathPeople.append(i)
                    deathPerson = sg.findNode(self.model, i.name)
                    deathPerson.childs = [self.gpuYellowQuad]
                
            elif i.day >= self.daysToHeal:
                number = np.random.uniform(0,1)
                number2 = np.random.uniform(0,1)
                self.sickPeople.remove(i)
                if number < self.healPbb:
                    self.healedPeople.append(i)
                    healedPerson = sg.findNode(self.model, i.name)
                    healedPerson.childs = [self.gpuGreenQuad]
                else:
                    self.healthPeople.append(i)
                    healthPerson = sg.findNode(self.model, i.name)
                    healthPerson.childs = [self.gpuBlueQuad]
            else:
                for j in self.healthPeople:
                    if not self.personalDistance(i,j):
                        num = np.random.uniform(0,1)
                        if num < self.countagiusPbb:
                            j.initialDay = time
                            self.healthPeople.remove(j)
                            self.sickPeople.append(j)
                            sickPerson = sg.findNode(self.model, j.name)
                            sickPerson.childs = [self.gpuRedQuad]
                           


    def randomMovement(self):
        for i in self.people:
            i.randomMovement()

    def update(self, time):
        self.randomMovement()
        self.spread(time)
        for i in self.sickPeople:
            i.update(time)
        
        if self.isParty:
            node = sg.findNode(self.model, 'background')
            node.childs = [es.toGPUShape(bs.createColorQuad(1,1,1))]
            for i in self.people:
                i.party()
            number = np.random.uniform(0,1)
            if number < 2*self.eventPbb:
                self.isParty = False
                node.childs = [es.toGPUShape(bs.createColorQuad(0.1,0.1,0.1))]

        if self.isQuarantine:
            for i in self.people:
                i.goHouse()


        
        
class Universe:
    def __init__(self, ratio, countagiusPbb, deathPbb, cardinality, daysToHeal, eventPbb =0.01, quarantineCriterion = 0.05):
        # Creating the communities
        community1 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 2.25,1.5, eventPbb,0.3)
        community2 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 2.25,0,eventPbb,0.3)
        community3 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 1,1.5,eventPbb,0.3)
        community4 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 1,0,eventPbb,0.3)
        community5 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 1,-1.5,eventPbb,0.3)
        community6 = Community(int(cardinality/6), ratio, countagiusPbb, deathPbb, daysToHeal, 2.25,-1.5,eventPbb,0.3)
      
        # Creating the gpu shapes
        gpuDay = es.toGPUShape(bs.createTextureQuad('textures/day.png'), GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuNumbers = []
        for i in range(10):
            gpuNumber = es.toGPUShape(bs.createTextureQuad('textures/' + str(i) + '.png'), GL_CLAMP_TO_EDGE, GL_LINEAR)
            gpuNumbers.append(gpuNumber)
        numbers = []
        for i in range(10):
            number = sg.SceneGraphNode(str(i))
            number.childs += [gpuNumbers[i]]
            numbers.append(number)

        # Creating the nodes

        day = sg.SceneGraphNode('day')
        day.transform = tr.scale(0.26/3, 0.17/3, 1)
        day.childs += [gpuDay]

        numberDay = sg.SceneGraphNode('numberDay')
        numberDay.transform = tr.translate(0.07,0,0)

        textureUniverse = sg.SceneGraphNode('textureUniverse')
        textureUniverse.transform = tr.translate(0.45,0.7,0)
        textureUniverse.childs += [day, numberDay]

        colorUniverse = sg.SceneGraphNode('colorUniverse')
        colorUniverse.childs += [community1.model, community2.model, community3.model, community4.model, community5.model, community6.model]

        universe = sg.SceneGraphNode('universe')
        universe.childs += [colorUniverse, textureUniverse]
        self.model = universe
        self.communities = [community1, community2, community3, community4, community5, community6]
        self.time = 0
        self.numbers = numbers
        self.previousDay = 0
        self.healthPeople = 0
        self.sickPeople = 0 
        self.deathPeople = 0
        self.healedPeople = 0
        self.cardinality = cardinality
        self.experiments = 6
        self.data = [[self.cardinality- self.experiments],[self.experiments],[0],[0]]
        self.dataTime = 0
        self.eventPbb = eventPbb
        self.quarantineCriterion = quarantineCriterion
        

    def draw(self, pipeline, texturePipeline):
        glUseProgram(pipeline.shaderProgram)
        colorUniverse = sg.findNode(self.model, 'colorUniverse')
        sg.drawSceneGraphNode(colorUniverse, pipeline, "transform")

        glUseProgram(texturePipeline.shaderProgram)
        textureUniverse = sg.findNode(self.model, 'textureUniverse')
        sg.drawSceneGraphNode(textureUniverse, texturePipeline, 'transform')
    
    def update(self, time):
        self.time = time
        self.day()
        health = 0
        sick = 0 
        death = 0
        healed = 0
        for community in self.communities:
            community.update(time)
            health += len(community.healthPeople)
            sick += len(community.sickPeople)
            death += len(community.deathPeople)
            healed += len(community.healedPeople)
        self.healthPeople = health
        self.sickPeople = sick
        self.deathPeople = death
        self.healedPeople = healed
        time = int(time)
        if self.dataTime < time:
            self.data[0].append(health)
            self.data[1].append(sick)
            self.data[2].append(death)
            self.data[3].append(healed)
            self.dataTime += 1
        self.party()
        self.quarantine()



    def day(self):
    
        day = int(self.time)
        if day > self.previousDay:
            day = str(day)
            digits = [int(d) for d in day]
            node = sg.findNode(self.model, 'numberDay')
            self.previousDay += 1
            number = []
            for digit in digits:
                if digit ==0:
                    number +=[self.numbers[0]]
                if digit ==1:
                    number +=[self.numbers[1]]
                if digit ==2:
                    number +=[self.numbers[2]]
                if digit ==3:
                    number +=[self.numbers[3]]
                if digit ==4:
                    number +=[self.numbers[4]]
                if digit ==5:
                    number +=[self.numbers[5]]
                if digit ==6:
                    number +=[self.numbers[6]]
                if digit ==7:
                    number +=[self.numbers[7]]
                if digit ==8:
                    number +=[self.numbers[8]]
                if digit ==9:
                    number +=[self.numbers[9]]
            x = 0
            for digit in number:
                digit.transform = tr.matmul([tr.uniformScale(0.2/3.5),tr.translate(0.7*x, 0, 0)])
                x += 1

            node.childs = number
    
    def graph(self):
        fig, ax = plt.subplots()
        days = np.arange(len(self.data[0]))
        ax.plot(days,self.data[0], label = 'Sanos')
        ax.plot(days,self.data[2], label = 'Muertos')
        ax.plot(days,self.data[3], label = 'Curados')
        ax.plot(days,self.data[1], label = 'Enfermos')        
        
        ax.set(xlabel='Dia', ylabel='Numero de personas',
            title='Estado de la población en función del tiempo')
        ax.grid()
        ax.legend()
        plt.show()

    def party(self):
        number = np.random.uniform(0,1)
        if number < self.eventPbb:
            community = random.choice(self.communities)
            if not community.isQuarantine:
                community.isParty = True

    def quarantine(self):
        for community in self.communities:
            if len(community.sickPeople) > self.quarantineCriterion*len(community.people):
                community.isQuarantine = True
            else:
                community.isQuarantine = False

class Figure:
    def __init__(self, cardinality):
        gpuRedQuad = es.toGPUShape(bs.createColorQuad(1,0,0))
        gpuBlueQuad = es.toGPUShape(bs.createColorQuad(0,0,1))
        gpuYellowQuad = es.toGPUShape(bs.createColorQuad(1,1,0))
        gpuGreenQuad = es.toGPUShape(bs.createColorQuad(0,1,0))

        gpuTittle = es.toGPUShape(bs.createTextureQuad('textures/tittle.png'),GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuHealth = es.toGPUShape(bs.createTextureQuad('textures/health.png'),GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuSick = es.toGPUShape(bs.createTextureQuad('textures/sick.png'),GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuDeath = es.toGPUShape(bs.createTextureQuad('textures/death.png'),GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuHealed = es.toGPUShape(bs.createTextureQuad('textures/healed.png'),GL_CLAMP_TO_EDGE, GL_LINEAR)
        gpuBackGround = es.toGPUShape(bs.createTextureQuad('textures/plotBackground.png'), GL_CLAMP_TO_EDGE, GL_LINEAR)

        sickPeople = sg.SceneGraphNode('sickPeople')
        sickPeople.transform = tr.matmul([tr.translate (0.5,0,0),tr.scale(0.5,1,1)])
        sickPeople.childs += [gpuRedQuad]

        healthPeople = sg.SceneGraphNode('healthPeople')
        healthPeople.transform = tr.matmul([tr.translate (0.5,0,0),tr.scale(0.5,1,1)])
        healthPeople.childs += [gpuBlueQuad]
        
        deathPeople = sg.SceneGraphNode('deathPeople')
        deathPeople.transform = tr.matmul([tr.translate (0.5,0,0),tr.scale(0.5,1,1)])
        deathPeople.childs += [gpuYellowQuad]

        healedPeople = sg.SceneGraphNode('healedPeople')
        healedPeople.transform = tr.matmul([tr.translate (0.5,0,0),tr.scale(0.5,1,1)])
        healedPeople.childs += [gpuGreenQuad]

        # Color legend

        blueQuad = sg.SceneGraphNode('blueQuad')
        blueQuad.transform = tr.matmul([tr.translate(-0.15,0.7,0), tr.uniformScale(0.1)])
        blueQuad.childs += [gpuBlueQuad]

        redQuad = sg.SceneGraphNode('redQuad')
        redQuad.transform = tr.matmul([tr.translate(-0.15,0.6,0), tr.uniformScale(0.1)])
        redQuad.childs += [gpuRedQuad]

        yellowQuad = sg.SceneGraphNode('yellowQuad')
        yellowQuad.transform = tr.matmul([tr.translate(-0.15,0.5,0), tr.uniformScale(0.1)])
        yellowQuad.childs += [gpuYellowQuad]

        greenQuad = sg.SceneGraphNode('greenQuad')
        greenQuad.transform = tr.matmul([tr.translate(-0.15,0.4,0), tr.uniformScale(0.1)])
        greenQuad.childs += [gpuGreenQuad]

        colorLegend = sg.SceneGraphNode('colorLegend')
        colorLegend.transform = tr.matmul([tr.translate(0.4,0.15,0), tr.uniformScale(0.7)])
        colorLegend.childs += [redQuad, blueQuad, yellowQuad, greenQuad]

        colorFigure = sg.SceneGraphNode('colorFigure')
        colorFigure.transform = tr.translate(-0.5,-0.5,0)
        colorFigure.childs += [healthPeople, sickPeople, deathPeople, healedPeople, colorLegend]
        
        
        tittle = sg.SceneGraphNode('tittle')
        tittle.transform = tr.matmul([tr.translate(0.1,0.65,0), tr.scale(0.274*3,0.024*3,1)])
        tittle.childs += [gpuTittle]

        # Texture Leyend
        health = sg.SceneGraphNode('textureHealth')
        health.transform = tr.matmul([tr.translate(0,0.2,0), tr.scale(0.41/2,0.2/2,1)])
        health.childs += [gpuHealth]

        sick = sg.SceneGraphNode('textureSick')
        sick.transform = tr.matmul([tr.translate(0.068,0.1,0), tr.scale(0.68/2,0.2/2,1)])
        sick.childs += [gpuSick]

        death = sg.SceneGraphNode('textureDeath')
        death.transform = tr.matmul([tr.translate(0.04,0,0), tr.scale(0.57/2,0.2/2,1)])
        death.childs += [gpuDeath]

        healed = sg.SceneGraphNode('textureHealed')
        healed.transform = tr.matmul([tr.translate(0.03,-0.09,0), tr.scale(0.54/2,0.16/2,1)])
        healed.childs += [gpuHealed]


        legend = sg.SceneGraphNode('legend')
        legend.transform = tr.matmul([tr.translate(0.4,0,0), tr.uniformScale(0.7)])
        legend.childs += [health, sick, death, healed]

        # Plot background
        plotBackground = sg.SceneGraphNode('plotBackGround')
        plotBackground.transform = tr.matmul([tr.translate(0.095,0.01,0), tr.scale(1,1.2,1)])
        plotBackground.childs += [gpuBackGround]

        textureFigure = sg.SceneGraphNode('textureFigure')
        textureFigure.transform = tr.translate(-0.5,0,0)
        textureFigure.childs += [plotBackground, tittle, legend]

        figure = sg.SceneGraphNode('figure')
        figure.childs += [textureFigure, colorFigure]

        self.model = figure 
        self.cardinality = cardinality
        
    
    def draw(self,pipeline,texturePipeline):
        colorFigure = sg.findNode(self.model, 'colorFigure')
        textureFigure = sg.findNode(self.model, 'textureFigure')

        glUseProgram(texturePipeline.shaderProgram)
        sg.drawSceneGraphNode(textureFigure, texturePipeline, 'transform')
        
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(colorFigure, pipeline, "transform")
        
    
    def update(self,health, sick, death, healed):
        sickPeople = sg.findNode(self.model,'sickPeople')
        sickPeople.transform = tr.matmul([tr.scale(0.1,sick/self.cardinality,1), tr.translate(-2,0.5,0)])
        healthPeople = sg.findNode(self.model,'healthPeople')
        healthPeople.transform = tr.matmul([tr.scale(0.1,health/self.cardinality,1), tr.translate(-1,0.5,0)])
        deathPeople = sg.findNode(self.model, 'deathPeople')
        deathPeople.transform = tr.matmul([tr.scale(0.1,death/self.cardinality,1), tr.translate(0,0.5,0)])
        healedPeople = sg.findNode(self.model, 'healedPeople')
        healedPeople.transform = tr.matmul([tr.scale(0.1,healed/self.cardinality,1), tr.translate(1,0.5,0)])

