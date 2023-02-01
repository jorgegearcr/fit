#!/usr/bin/env python3
# -*- coding:utf-8 -*-
######
# -----
# MIT License
# 
# Copyright (c) 2022 FIT-Project and others
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----
###### 

from model.db import Db

from sqlalchemy import  Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


class ScreenRecorder(Base):

    __tablename__ = 'configuration_screenrecorder'
    
    id = Column(Integer, primary_key = True)
    enabled = Column(Boolean)
    resolution_width = Column(Integer)
    resolution_height = Column(Integer)
    codec_id = Column(Integer)
    fps = Column(Integer)
    filename = Column(String)
    
    def __init__(self) -> None:
        super().__init__()
        self.db = Db()
        self.metadata.create_all(self.db.engine)
    
    def get(self):
        if self.db.session.query(ScreenRecorder).first() is None:
            self.set_default_values()
            
        return self.db.session.query(ScreenRecorder).all()
    
    def update(self, options):
        self.db.session.query(ScreenRecorder).filter(ScreenRecorder.id == options.get('id')).update(options)
        self.db.session.commit()
    
    def set_default_values(self):
        
        self.enabled = True
        self.resolution_width = 1920
        self.resolution_height = 1080
        self.codec_id = 1
        self.fps = 25
        self.filename = "acquisition.avi"
        
        self.db.session.add(self)
        self.db.session.commit()