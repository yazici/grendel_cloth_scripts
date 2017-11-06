#Authors: Daniel Fuller, Trevor Barrus, Brennan Mitchell
import os

import maya
import maya.mel as mel #Allows for evaluation of MEL
import pymel.core as pc #Allows for evaluation of MEL (NECESSARY?)
import maya.cmds as mc

from byuam.project import Project
from byuam.environment import Department, Environment

STARTANIM = -5
STARTPRE = -25

#########################
## ESTABLISH CFX SCENE ##
#########################

#This code is brought to you in part by Trevor Barrus and the letter G

def generateScene():
    project = Project()
    environment = Environment()

    # Create a global position locator for Beowulf's Starting Location
    mc.currentTime(STARTANIM)
    globalPos = mc.spaceLocator(p=[0,0,0])
    globPos = mc.rename(globalPos, "beowulfGlobalPos")
    mc.select("grendel_rig_main_Beowulf_primary_global_cc_01")
    mc.select(globPos, add=True)
    mc.pointConstraint(offset=[0,0,0], weight=1)
    mc.orientConstraint(offset=[0,0,0], weight=1)

    # Get transformation variables from globPos locator
    tx = mc.getAttr(globPos+".translateX")
    ty = mc.getAttr(globPos+".translateY")
    tz = mc.getAttr(globPos+".translateZ")
    rx = mc.getAttr(globPos+".rotateX")
    ry = mc.getAttr(globPos+".rotateY")
    rz = mc.getAttr(globPos+".rotateZ")

    # get alembic filepath for scene's animation (requires prior export)
    src = mc.file(q=True, sceneName=True)
    src_dir = os.path.dirname(src)
    checkout_element = project.get_checkout_element(src_dir)
    checkout_body_name = checkout_element.get_parent()
    body = project.get_body(checkout_body_name)
    element = body.get_element(Department.ANIM)
    cache_file = os.path.join(element.get_dir(), "cache", "beowulf_rig_main.abc")

    # checkout cfx scene for corresponding shot number
    current_user = environment.get_current_username()
    element = body.get_element(Department.CFX)
    cfx_filepath = element.checkout(current_user)

    #open cfx file 
    if cfx_filepath is not None:
        if not mc.file(q=True, sceneName=True) == '':
            mc.file(save=True, force=True) #save file

        if not os.path.exists(cfx_filepath):
            mc.file(new=True, force=True)
            mc.file(rename=cfx_filepath)
            mc.file(save=True, force=True)
        else:
            mc.file(cfx_filepath, open=True, force=True)

    # import alembic
    command = "AbcImport -mode import \"" + cache_file + "\""
    maya.mel.eval(command)

    # delete all geo except ten's skin and rename
    geometry = mc.ls(geometry=True)
    transforms = mc.listRelatives(geometry, p=True, path=True)
    mc.select(transforms, r=True)
    for geo in mc.ls(sl=True):
        if(geo != "ten_rig_main_Ten_Skin_RENDER"):
            mc.delete(geo)
    collide = "TEN_ANIM"
    mc.rename("ten_rig_main_Ten_Skin_RENDER", collide)

    # Reference Beowulf's Sim Robe
    body = project.get_body("beowulf_robe_sim")
    element = body.get_element(Department.MODEL)
    robe_file = element.get_app_filepath()
    mc.file(robe_file, reference=True)
    
    # Reference Beowulf's Beauty/Hero Robe
    body = project.get_body("beowulf_robe")
    element = body.get_element(Department.MODEL)
    robe_hero_file = element.get_app_filepath()
    mc.file(robe_hero_file, reference=True)
    
    # Set Sim Robe transforms to variables above
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.translateX", tx)
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.translateY", ty)
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.translateZ", tz)
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.rotateX", rx)
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.rotateY", ry)
    mc.setAttr("ten_robe_sim_model_main_ten_cloth.rotateZ", rz)
    
    # Set Hero Robe transforms to variables above
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.translateX", tx)
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.translateY", ty)
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.translateZ", tz)
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.rotateX", rx)
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.rotateY", ry)
    mc.setAttr("ten_robe_model_main_TEN_ROBE_HERO.rotateZ", rz)
    



#######################
##       MAIN        ##
#######################

generateScene()

#######################
## Set Up Simulation ##
#######################

mc.select('ten_robe_sim_model_main_ten_collide_body', replace=True)
mc.viewFit() #Snap View to Body Collider
mc.playbackOptions(animationStartTime=STARTPRE)
mc.playbackOptions(minTime=STARTPRE)
mc.currentTime(STARTPRE)

#Wrap Colliders to Alembic
mc.select('ten_robe_sim_model_main_ten_collide_body', replace=True) #Wrap Body
mc.select('TEN_ANIM', add=True)
mc.CreateWrap()
#mc.setAttr('wrap1.exclusiveBind', 0)

mc.select('ten_robe_sim_model_main_ten_collide_mitten_l', replace=True) #Wrap Left Mitten
mc.select('TEN_ANIM', add=True)
mc.CreateWrap()
#mc.setAttr('wrap2.exclusiveBind', 0)

mc.select('ten_robe_sim_model_main_ten_collide_mitten_r', replace=True) #Wrap Right Mitten
mc.select('TEN_ANIM', add=True)
mc.CreateWrap()
#mc.setAttr('wrap3.exclusiveBind', 0)

#Establish Colliders
mc.select('ten_robe_sim_model_main_ten_collide_body', replace=True) #Collider Body
mel.eval('makeCollideNCloth;')

mc.select('ten_robe_sim_model_main_ten_collide_mitten_l', replace=True) #Collider Left Mitten
mel.eval('makeCollideNCloth;')

mc.select('ten_robe_sim_model_main_ten_collide_mitten_r', replace=True) #Collider Right Mitten
mel.eval('makeCollideNCloth;')

#Establish nCloth Objects
mc.select('ten_robe_sim_model_main_ten_sim_robe', replace=True) #nCloth: Robe
mel.eval('createNCloth 0;')

mc.setAttr('nClothShape1.thickness', 0.003) #Collision Properties: Robe
mc.setAttr('nClothShape1.selfCollideWidthScale', 5.0)
mc.setAttr('nClothShape1.friction', 0.0)
mc.setAttr('nClothShape1.stickiness', 0.1)

mc.setAttr('nClothShape1.stretchResistance', 200.0) #Dynamic Properties: Robe
mc.setAttr('nClothShape1.compressionResistance', 100.0)
mc.setAttr('nClothShape1.bendResistance', 1.0)
mc.setAttr('nClothShape1.damp', 0.8)

mc.select('ten_robe_sim_model_main_ten_sim_pants', replace=True) #nCloth: Pants
mel.eval('createNCloth 0;')

mc.setAttr('nClothShape2.thickness', 0.003) #Collision Properties: Pants
mc.setAttr('nClothShape2.selfCollideWidthScale', 5.0)
mc.setAttr('nClothShape2.friction', 0.0)
mc.setAttr('nClothShape2.stickiness', 0.1)

mc.setAttr('nClothShape2.stretchResistance', 200.0) #Dynamic Properties: Pants
mc.setAttr('nClothShape2.compressionResistance', 100.0)
mc.setAttr('nClothShape2.bendResistance', 1.0)
mc.setAttr('nClothShape2.damp', 0.8)

#### Establish Dynamic Constraints ####

# These are correct for Beowulf's cape beauty mesh
mc.select(clear=True) #neckline Constraints
cape_neckline_verts = ['[396:398]', '[403]', '[404]', '[409]', '[410]', '[415]', '[416]', '[421]', '[422]', '[427]', '[1499]', '[1502]', '[1510]', '[1512]', '[1520]', '[1522]', '[1530]', '[1532]', '[1540]', '[1542]', '[1550]', '[1552]', '[8524]', '[8530]', '[8531]', '[8546]', '[8547]', '[8550]', '[8551]', '[8566]', '[8567]', '[8570]', '[8571]', '[8586]', '[8587]', '[8590]', '[8591]', '[8606]', '[8607]', '[8611]', '[8610]', '[8627]', '[8626]', '[8630]', '[8631]' ]


for i in cape_neckline_verts:
    mc.select('ten_robe_sim_model_main_ten_sim_robe.vtx' + i, add=True)
mc.select('ten_robe_sim_model_main_ten_collide_body', add=True)
mel.eval('createNConstraint pointToSurface 0;')


# These are correct for Beowulf's cape beauty mesh
mc.select(clear=True) #front Constraints
cape_front_verts = [ '[4950]', '[4951]', '[4954]', '[4955]', '[4998]', '[4999]', '[5010]', '[5011]', '[5015]', '[5018]', '[5019]', '[5022]', '[5026]', '[5027]', '[7712]', '[7716]', '[7760]', '[7772]', '[7780]', '[7784]', '[7788]', '[10731]', '[10732]', '[10757]', '[10758]', '[10764]', '[10767]' ]


for i in robe_front_verts:
    mc.select('ten_robe_sim_model_main_ten_sim_robe.vtx' + i, add=True)
mc.select('ten_robe_sim_model_main_ten_collide_body', add=True)
mel.eval('createNConstraint pointToSurface 0;') 




#Set Nucleus Parameters (INCOMPLETE - New Nucleus specific to Ten?)
mc.setAttr('nucleus1.subSteps', 15)
mc.setAttr('nucleus1.maxCollisionIterations', 20)
mc.setAttr('nucleus1.startFrame', STARTPRE)
mc.setAttr('nucleus1.spaceScale', 0.45)

#########################
## PREPARE HERO MESHES ##
#########################

#Create Sleeveless Robe for Sash Sim
mc.duplicate('ten_robe_model_main_ten_Hero_Robe')
mc.rename('ten_robe_model_main_ten_Hero_Robe1', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless')

mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1861:1862]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1866:1869]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1872:1873]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1878:1881]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1884:1885]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1888]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1891]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1893:1894]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1898:1899]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2009:2010]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2021:2022]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2396:2397]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2402:2403]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2412]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2415]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[2428:2429]', replace=True)
mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[968]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[971:972]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[975:976]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[979:980]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[983:984]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[987:988]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[991:992]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[995:996]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[999:1000]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1003:1004]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1007:1008]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1011:1012]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1015:1016]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1019:1020]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1023:1024]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1027:1028]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[1031]', add=True)
mc.delete()

mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[0:895]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[4452:4579]', replace=True)
mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[968:1639]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[3872:3935]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[4000:4127]', 'ten_robe_model_main_ten_Hero_Robe_Sleeveless.f[4324:4451]', add=True)
mc.delete()

# Wrap Hero Meshes to Sim Meshes
mc.select('ten_robe_model_main_ten_Hero_Robe', replace=True) #Wrap Robe
mc.select('ten_robe_sim_model_main_ten_sim_robe', add=True)
mc.CreateWrap()
#mc.setAttr('wrap4.exclusiveBind', 0)

mc.select('ten_robe_model_main_ten_Hero_Pants', replace=True) #Wrap Pants
mc.select('ten_robe_sim_model_main_ten_sim_pants', add=True)
mc.CreateWrap()
#mc.setAttr('wrap5.exclusiveBind', 0)

mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless', replace=True) #Wrap Sleeveless Robe (Exclusive Bind)
mc.select('ten_robe_model_main_ten_Hero_Robe', add=True)
mc.CreateWrap()
#mc.setAttr('wrap6.exclusiveBind', 1)

mc.select('ten_robe_model_main_ten_Hero_Sash', replace=True) #Wrap Sash
mc.select('ten_robe_model_main_ten_Hero_Robe_Sleeveless', add=True)
mc.CreateWrap()
#mc.setAttr('wrap7.exclusiveBind', 0)

#Rename/Group Simulation Objects
mc.rename('nucleus1', 'nucleus_ten') #Nucleus

mc.rename('nRigid1', 'nRigid_ten_body') #nRigid
mc.rename('nRigid2', 'nRigid_ten_mitten_l')
mc.rename('nRigid3', 'nRigid_ten_mitten_r')
mc.group('nRigid_ten_body', 'nRigid_ten_mitten_l', 'nRigid_ten_mitten_r', name='ten_nRigid')

mc.rename('nCloth1', 'nCloth_ten_robe') #nCloth
mc.rename('nCloth2', 'nCloth_ten_pants')
mc.group('nCloth_ten_robe', 'nCloth_ten_pants', name='ten_nCloth')

mc.rename('dynamicConstraint1', 'dynamicConstraint_ten_robe_lapel') #dynamicConstraint
mc.rename('dynamicConstraint2', 'dynamicConstraint_ten_robe_back')
mc.rename('dynamicConstraint3', 'dynamicConstraint_ten_robe_front')
mc.rename('dynamicConstraint4', 'dynamicConstraint_ten_pants')
mc.group('dynamicConstraint_ten_robe_lapel', 'dynamicConstraint_ten_robe_back', 'dynamicConstraint_ten_robe_front', 'dynamicConstraint_ten_pants', name='ten_dynamicConstraint')

mc.group('nucleus_ten', 'ten_nRigid', 'ten_nCloth', 'ten_dynamicConstraint', name='ten_simulation')

#Group Alembic Objects
mc.group('TEN_ANIM', 'TEN_ANIMBase', 'TEN_ANIMBase1', 'TEN_ANIMBase2', name='ten_alembic')

#Group Ten Cloth
mc.group('ten_robe_sim_model_main_ten_cloth', 'ten_robe_model_main_TEN_ROBE_HERO', 'ten_simulation', 'ten_alembic', name='ten_cloth')

#Hide Unnescessary Objects
mc.hide('ten_simulation')
mc.hide('ten_robe_sim_model_main_ten_cloth')
