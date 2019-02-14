FROM docker.lundalogik.com/lundalogik/crm/app

COPY . /lime/plugin/plugin_objektvision

RUN limeplug install /lime/plugin/plugin_objektvision
