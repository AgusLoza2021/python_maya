import maya.cmds as mc
for module_name in sys.modules.keys():
    top_module = module_name.split('.'[0])
    if top_module == 'jaw_utils':
        del(sys.modules[module_name])
''' 
0.7 , 0.5 , 0.5
'''
GROUP = 'GROUP'
JOINT = 'JNT'
GUIDE = 'guide'
JAW = 'jaw'
LEFT = 'L'
RIGHT = 'R'
CENTER = 'C'
number = 5
jaw_guide_grp = None

def createUI():
    if mc.window('LipAutoRigg', exists=True):
        mc.deleteUI('LipAutoRigg')

    window = mc.window('LipAutoRigg', title='Lip Auto Rigg', widthHeight=(650, 350),bgc=(0.6,.5,.6))
    mc.columnLayout(adjustableColumn=True)

    mc.text(label='LIP_AUTORIGG', align='center', font='boldLabelFont')
    mc.separator(height=15, style='none')
    mc.separator(height=15, style='none')

    mc.text(label=' INSERT YOURS LOCS FOR JNTS FOR SIDES')
    num_guides_field = mc.intField(value=number, minValue=1, width=100)
    mc.separator(height=12, style='none')

    mc.button(label='Create Locators', command=lambda x: createGuides(mc.intField(num_guides_field, q=True, value=True)),bgc=(.7,.5,0.5))
    mc.separator(height=20, style='none')

    mc.button(label='build', command=lambda x: build(),bgc=(.7,.5,0.5))
    mc.separator(height=15, style='none')


    mc.button(label='Close', command=('mc.deleteUI(\"LipAutoRigg\", window=True)'), bgc=(0.5, 0.2, 0.2))
    mc.separator(height=22, style="none")

    mc.showWindow(window)


def createGuides(number=5):

    global jaw_guide_grp 
    jaw_guide_grp = mc.group(em=True, name='{}_{}_{}_{}'.format(CENTER, JAW, GUIDE, GROUP))
    locs_grp = mc.group(em=True, name='{}_{}_lip_{}_{}'.format(CENTER, JAW, GUIDE, GROUP), parent=jaw_guide_grp)
    lip_locs_grp = mc.group(em=True, name='{}_lipMinor_{}_{}'.format(CENTER, GUIDE, GROUP), parent=locs_grp)
   
    for part in ['Upper', 'Lower']:
        part_mult = 1 if part == 'Upper' else -1
        mid_data = (0, part_mult, 0)

        mid_loc = mc.spaceLocator(name='{}_{}{}_lip_{}'.format(CENTER, JAW, part, GUIDE))[0]
        mc.parent(mid_loc, lip_locs_grp)

        for side in 'LR':
            for x in range(number):
                multiplier = x + 1 if side == 'R' else -(x + 1)
                loc_data = (multiplier, part_mult, 0)
                loc = mc.spaceLocator(name='{}_{}{}_lip_{:02d}_{}'.format(side, JAW, part, x+1, GUIDE))[0]
                mc.parent(loc, lip_locs_grp)
                mc.setAttr('{}.t'.format(loc), *loc_data)
               
        
        mc.setAttr('{}.t'.format(mid_loc), *mid_data)
    
    for side in [LEFT, RIGHT]:
        corner_loc = mc.spaceLocator(name='{}_{}Corner_lip_{}'.format(side, JAW, GUIDE))[0]
        mc.parent(corner_loc, lip_locs_grp)        
        if side == LEFT:
            mc.setAttr('{}.t'.format(corner_loc), *(number + 1, 0, 0))
        else:
            mc.setAttr('{}.t'.format(corner_loc), *(-(number + 1), 0, 0))
    
    mc.select(cl=True)

    jaw_base_guide = mc.group(em=True, name='{}_{}_base_{}_{}'.format(CENTER, JAW, GUIDE, GROUP), parent=jaw_guide_grp)
    jaw_guide = mc.spaceLocator(name='loc_jaw_guide')[0]
    jaw_inverse_guide = mc.spaceLocator(name='loc_inverse_jaw_guide')[0]

    mc.setAttr('{}.t'.format(jaw_guide), *(0, 1, -number))
    mc.setAttr('{}.t'.format(jaw_inverse_guide), *(0, -1, -number))

    mc.parent(jaw_guide, jaw_base_guide)
    mc.parent(jaw_inverse_guide, jaw_base_guide)

# creamos herarquia para grps

def createHierarchyAndJoints(*args):
    main_grp = mc.group(em=True, name='{}_{}_rig_{}'.format(CENTER, JAW, GROUP))
    mc.group(em=True, name='{}_{}Lip_{}'.format(CENTER, JAW, GROUP), parent=main_grp)
    mc.group(em=True, name='{}_{}Base_{}'.format(CENTER, JAW, GROUP), parent=main_grp)
    mc.group(em=True, name='{}_{}Lip_minor_{}'.format(CENTER, JAW, GROUP), parent=main_grp)
    mc.group(em=True, name='{}_{}Lip_broad_{}'.format(CENTER, JAW, GROUP), parent=main_grp)

    

# creamos lip guides como grps
def lip_guides():
    grp = '{}_lipMinor_{}_{}'.format(CENTER, GUIDE, GROUP)
    return [loc for loc in mc.listRelatives(grp) if mc.objExists(loc)]

def jaw_guides():
    grp = '{}_{}_{}_{}'.format(CENTER, JAW, GUIDE, GROUP)
    return [loc for loc in mc.listRelatives(grp) if mc.objExists(loc)]


# creamos los jnts 
def createMinorJoints():
    for guide in lip_guides():
        mat = mc.xform(guide, q=True, m=True, ws=True)
        jnt = mc.joint(name=guide.replace(GUIDE, JOINT))
        mc.setAttr('{}.radius'.format(jnt), 0.5)
        mc.xform(jnt, m=mat, ws=True)
        mc.parent(jnt, '{}_{}Lip_minor_{}'.format(CENTER, JAW, GROUP))

# creamos los broad joints
def createBroadJoints():
    upper_joint = mc.joint(name='{}_{}_broadUpper_{}'.format(CENTER, JAW, JOINT))
    lower_joint = mc.joint(name='{}_{}_broadLower_{}'.format(CENTER, JAW, JOINT))
    left_joint = mc.joint(name='{}_{}_broadCorner_{}'.format(LEFT, JAW, JOINT))
    right_joint = mc.joint(name='{}_{}_broadCorner_{}'.format(RIGHT, JAW, JOINT))

    mc.parent([upper_joint, lower_joint, left_joint, right_joint], '{}_{}Lip_broad_{}'.format(CENTER, JAW, GROUP))

    upper_pos = mc.xform('{}_{}Upper_lip_{}'.format(CENTER, JAW, GUIDE), q=True, m=True, ws=True)
    lower_pos = mc.xform('{}_{}Lower_lip_{}'.format(CENTER, JAW, GUIDE), q=True, m=True, ws=True)
    left_pos = mc.xform('{}_{}Corner_lip_{}'.format(LEFT, JAW, GUIDE), q=True, m=True, ws=True)
    right_pos = mc.xform('{}_{}Corner_lip_{}'.format(RIGHT, JAW, GUIDE), q=True, m=True, ws=True)

    mc.xform(upper_joint, m=upper_pos)
    mc.xform(lower_joint, m=lower_pos)
    mc.xform(left_joint, m=left_pos)
    mc.xform(right_joint, m=right_pos)

    mc.select(cl=True)


# creamos base para Jaw
def createJawBase():
    base_name = '{}_{}Base_{}'.format(CENTER, JAW, GROUP)
    if not mc.objExists(base_name):
        mc.group(em=True, name=base_name)

    guides = jaw_guides()
    if len(guides) < 2:
        print('dont have jawbase guides')
        return
    jaw_jnt = mc.joint(name='{}_{}_{}'.format(CENTER, JAW, JOINT))
    jaw_inverse_jnt = mc.joint(name='{}_inverse_{}_{}'.format(CENTER, JAW, JOINT))

    mc.xform(jaw_jnt, m=mc.xform(guides[0], q=True, m=True, ws=True), ws=True)
    mc.xform(jaw_inverse_jnt, m=mc.xform(guides[1], q=True, m=True, ws=True), ws=True)

    mc.parent(jaw_jnt, base_name)
    mc.parent(jaw_inverse_jnt, base_name)
    mc.select(cl=True)

    # Hacer que los joints sean hijos de los locators
    loc_jaw_guide = mc.ls('loc_jaw_guide')[0]
    loc_inverse_jaw_guide = mc.ls('loc_inverse_jaw_guide')[0]
    mc.parent(jaw_jnt, loc_jaw_guide)
    mc.parent(jaw_inverse_jnt, loc_inverse_jaw_guide)



def constraintBroadJoints():
    # Definir los nombres de los objetos
    jaw_joint = '{}_{}_{}'.format(CENTER, JAW, JOINT)
    inverse_jaw_joint = '{}_inverse_{}_{}'.format(CENTER, JAW, JOINT)
    broad_upper = '{}_{}_broadUpper_{}'.format(CENTER, JAW, JOINT)
    broad_lower = '{}_{}_broadLower_{}'.format(CENTER, JAW, JOINT)
    broad_left = '{}_{}_broadCorner_{}'.format(LEFT, JAW, JOINT)
    broad_right = '{}_{}_broadCorner_{}'.format(RIGHT, JAW, JOINT)
    
    # Aplicar restricciones de padres
    mc.parentConstraint(jaw_joint, broad_lower, mo=True)
    mc.parentConstraint(inverse_jaw_joint, broad_upper, mo=True)
    mc.parentConstraint(broad_upper, broad_lower, broad_left, mo=True)
    mc.parentConstraint(broad_upper, broad_lower, broad_right, mo=True)
    
    mc.select(cl=True)



def getLipParts(part=None):
    upper_token = 'jawUpper'
    lower_token = 'jawLower'
    corner_token = 'JawCorner'

    C_upper = '{}_{}_broadUpper_{}'.format(CENTER, JAW, JOINT)
    C_lower = '{}_{}_broadLower_{}'.format(CENTER, JAW, JOINT)
    L_corner = '{}_{}_broadLower_{}'.format(LEFT, JAW, JOINT)
    R_corner = '{}_{}_broadLower_{}'.format(RIGHT, JAW, JOINT)

    lip_joints = mc.listRelatives('{}_{}_rig_{}'.format(CENTER, JAW, GROUP), allDescendents=True)

    if lip_joints is not None:
        lookUp = {'C_upper': {}, 'C_lower': {},
                  'L_upper': {}, 'L_lower': {},
                  'R_upper': {}, 'R_lower': {},
                  'L_corner': {}, 'R_corner': {}}

        for joint in lip_joints:
            if mc.objectType(joint) != 'joint':
                continue

            if joint.startswith('C') and upper_token in joint:
                lookUp['C_upper'][joint] = [C_upper]

            if joint.startswith('C') and lower_token in joint:
                lookUp['C_lower'][joint] = [C_lower]

            if joint.startswith('L') and upper_token in joint:
                lookUp['L_upper'][joint] = [C_upper, L_corner]

            if joint.startswith('L') and lower_token in joint: 
                lookUp['L_lower'][joint] = [C_lower, L_corner]

            if joint.startswith('R') and upper_token in joint:
                lookUp['R_upper'][joint] = [C_upper, R_corner]

            if joint.startswith('R') and lower_token in joint:
                lookUp['R_lower'][joint] = [C_lower, R_corner]

            if joint.startswith('L') and corner_token in joint:
                lookUp['L_corner'][joint] = [L_corner]

            if joint.startswith('R') and corner_token in joint:
                lookUp['R_corner'][joint] = [R_corner]

        if part:
            return lookUp[part]
        else:
            return lookUp
    else:
        return {}


def lipPart(part):
    """
    :param part:
    :return:
    """

    lip_parts =  [reversed(sorted(getLipParts()['L_{}'.format(part)].keys())),
                  getLipParts()['C_{}'.format(part)].keys(),
                  sorted(getLipParts()['R_{}'.format(part)].keys())]
    
    return [joint for joint in lip_parts for joint in joint]


def createSeal(part):
    seal_name = '{}_seal_{}'.format(CENTER, GROUP)
    seal_parent = seal_name if mc.objExists(seal_name) else mc.createNode('transform', name=seal_name)

    part_grp = mc.createNode('transform', name=seal_name.replace('seal', 'seal_{}'.format(part)), parent=seal_parent)

    l_corner = '{}_{}_broadCorner_{}'.format(LEFT, JAW, JOINT)
    r_corner = '{}_{}_broadCorner_{}'.format(RIGHT, JAW, JOINT)

    value = len(lipPart(part))

    for index, joint in enumerate(lipPart(part)):
        node = mc.createNode('transform', name=joint.replace('JNT', '{}.SEAL'.format(part)), parent=part_grp)
        mat = mc.xform(joint, q=True, m=True, ws=True)
        mc.xform(node, m=mat, ws=True)

        constraint = mc.parentConstraint(l_corner, r_corner, node, mo=True)[0]
        mc.setAttr('{}.interpType'.format(constraint), 2)


        l_corner_value = float(index) / float(value - 1)
        r_corner_value = 1 - l_corner_value

        l_corner_attr = '{}.{}W0'.format(constraint, l_corner)
        r_corner_attr = '{}.{}W1'.format(constraint, r_corner)

        mc.setAttr(l_corner_attr, l_corner_value)
        mc.setAttr(r_corner_attr, r_corner_value)

        
        mc.select (cl=True)



def createJawAttrs():
# Nombre del nodo padre
    parent_node_name = '{}_{}_rig_{}'.format(CENTER, JAW, GROUP)

 # Verificar si el nodo padre existe
    if not mc.objExists(parent_node_name):
        mc.createNode('transform', name=parent_node_name)

# Verificar si el nodo para los atributos ya existe
    if mc.objExists('jaw_attributes'):
        node = 'jaw_attributes'
    else:
# Crear el nodo para los atributos si no existe
        node = mc.createNode('transform', name='jaw_attributes', parent=parent_node_name)

    lip_parts = getLipParts()

# Añadir atributos para 'C_upper'
    if 'C_upper' in lip_parts and lip_parts['C_upper']:
        first_upper = sorted(lip_parts['C_upper'].keys())[0]
        if not mc.attributeQuery(first_upper, node=node, exists=True):
            mc.addAttr(node, ln=first_upper, min=0, max=1, dv=0)
            mc.setAttr('{}.{}'.format(node, first_upper), lock=1)

# Añadir atributos para 'L_upper'
    for upper in sorted(lip_parts.get('L_upper', {}).keys()):
        if not mc.attributeQuery(upper, node=node, exists=True):
            mc.addAttr(node, ln=upper, min=0, max=1)

# Añadir atributos para 'L_corner'
    if 'L_corner' in lip_parts and lip_parts['L_corner']:
        first_corner = sorted(lip_parts['L_corner'].keys())[0]
        if not mc.attributeQuery(first_corner, node=node, exists=True):
            mc.addAttr(node, ln=first_corner, min=0, max=1, dv=1)
            mc.setAttr('{}.{}'.format(node, first_corner), lock=1)

# Añadir atributos para 'L_lower'
    for lower in sorted(lip_parts.get('L_lower', {}).keys())[::-1]:
        if not mc.attributeQuery(lower, node=node, exists=True):
            mc.addAttr(node, ln=lower, min=0, max=1, dv=0)

# Añadir atributos para 'C_lower'
    if 'C_lower' in lip_parts and lip_parts['C_lower']:
        first_lower = sorted(lip_parts['C_lower'].keys())[0]
        if not mc.attributeQuery(first_lower, node=node, exists=True):
            mc.addAttr(node, ln=first_lower, min=0, max=1, dv=0)
            mc.setAttr('{}.{}'.format(node, first_lower), lock=1)

    # Añadir atributos para 'R_upper'
    if 'R_upper' in lip_parts and lip_parts['R_upper']:
        first_upper = sorted(lip_parts['R_upper'].keys())[0]
        if not mc.attributeQuery(first_upper, node=node, exists=True):
            mc.addAttr(node, ln=first_upper, min=0, max=1, dv=0)
            mc.setAttr('{}.{}'.format(node, first_upper), lock=1)

    # Añadir atributos para 'R_upper'
    for upper in sorted(lip_parts.get('R_upper', {}).keys()):
        if not mc.attributeQuery(upper, node=node, exists=True):
            mc.addAttr(node, ln=upper, min=0, max=1)

    # Añadir atributos para 'R_corner'
    if 'R_corner' in lip_parts and lip_parts['R_corner']:
        first_corner = sorted(lip_parts['R_corner'].keys())[0]
        if not mc.attributeQuery(first_corner, node=node, exists=True):
            mc.addAttr(node, ln=first_corner, min=0, max=1, dv=1)
            mc.setAttr('{}.{}'.format(node, first_corner), lock=1)

    # Añadir atributos para 'R_lower'
    for lower in sorted(lip_parts.get('R_lower', {}).keys())[::-1]:
        if not mc.attributeQuery(lower, node=node, exists=True):
            mc.addAttr(node, ln=lower, min=0, max=1, dv=0)

    # Añadir atributos para 'C_lower'
    if 'C_lower' in lip_parts and lip_parts['C_lower']:
        first_lower = sorted(lip_parts['C_lower'].keys())[0]
        if not mc.attributeQuery(first_lower, node=node, exists=True):
            mc.addAttr(node, ln=first_lower, min=0, max=1, dv=0)
            mc.setAttr('{}.{}'.format(node, first_lower), lock=1)
            
            
def createInitialValues(part, degree=1.3):
    jaw_attr = [part for part in lipPart(part) if not part.startswith('C') and not part.startswith('R')]
    value = len(jaw_attr)

    for index, attr_name in enumerate(jaw_attr[::-1]):
        attr = 'jaw_attributes.{}'.format(attr_name)

        linear_value = float(index) / float(value - 1)
        div_value = linear_value / degree
        final_value = div_value * linear_value

        mc.setAttr(attr, final_value)

    mc.select(cl=True)



'''
def createConstraints():
    lip_parts = getLipParts()
    for part, value in lip_parts.items():
        for lip_jnt, broad_jnt in value.items():
            print("Processing:", lip_jnt, broad_jnt)  # Debug print

            seal_token = 'upper_SEAL' if 'Upper' in lip_jnt else 'lower_SEAL'
            lip_seal = lip_jnt.replace('JNT', seal_token)
            print("Seal Token:", seal_token)  # Debug print
            print("Lip Seal:", lip_seal)  # Debug print

            if not mc.objExists(lip_seal):
                const = mc.parentConstraint(broad_jnt, lip_seal, lip_jnt, mo=True)[0]
                mc.setAttr('{}.interpType'.format(const), 2)
                print("Created constraint:", const)  # Debug print
            else:
                const = mc.parentConstraint(broad_jnt, lip_jnt, mo=True)[0]
                mc.setAttr('{}.interpType'.format(const), 2)
                print("Constraint exists, created new constraint:", const)  # Debug print

            if len(broad_jnt) == 1:
                seal_attr = '{}_parentConstraint1.{}W0'.format(lip_jnt, 'C_jaw_broadUpper_JNT')
                rev = mc.createNode('reverse', name=lip_jnt.replace('JNT', 'REV'))
                mc.connectAttr(seal_attr, '{}.inputX'.format(rev))
                mc.connectAttr('{}.outputX'.format(rev), '{}_parentConstraint1.{}W0'.format(lip_jnt, broad_jnt[0]))
                mc.setAttr(seal_attr, 0)
                
                connections = mc.listConnections('{}_parentConstraint1.{}W1'.format(lip_jnt, 'C_jaw_broad_Upper_JNT'), source=True)
                if connections:
                    print("Connection established correctly.")

            if len(broad_jnt) == 2:
                seal_attr = '{}_parentConstraint1.{}W2'.format(lip_jnt, 'C_jaw_broad_Upper_JNT')
                mc.setAttr(seal_attr, 0)
                print("Set seal attribute to 0 for two joints.")  # Debug print

                seal_rev = mc.createNode('reverse', name=lip_jnt.replace('JNT', 'seal_REV'))
                jaw_attr_rev = mc.createNode('reverse', name=lip_jnt.replace('JNT', 'jaw_attr_REV'))
                seal_mult = mc.createNode('multiplyDivide', name=lip_jnt.replace('JNT', 'seal_MULT'))

                mc.connectAttr(seal_attr, '{}.inputX'.format(seal_rev))
                mc.connectAttr('{}.outputX'.format(seal_rev), '{}.input2X'.format(seal_mult))
                mc.connectAttr('{}.outputX'.format(seal_rev), '{}.input2Y'.format(seal_mult))

                jaw_attr = 'jaw_attributes.{}'.format(lip_jnt.replace(lip_jnt[0], 'L'))
                mc.connectAttr(jaw_attr, '{}.input1X'.format(seal_mult))
                mc.connectAttr(jaw_attr, '{}.input1Y'.format(seal_mult))

                mc.select(cl=True)
                

'''

def build():
    createHierarchyAndJoints()
    createMinorJoints()
    createBroadJoints()
    createJawBase()
    lip_guides()
    jaw_guides()
    getLipParts()
    lipPart('lower')
    lipPart('upper')
    createSeal('lower')
    createSeal('upper')
    createJawAttrs()
    createInitialValues('lower')
    createInitialValues('upper')


createUI()


