"""Original sentinel motion, shared by the full rig build and animation-only updates.

Blender coordinates: Z up, -Y forward. Leg targets use a two-link sagittal solve;
the root never translates during locomotion. No external animation assets.
"""
import math
from mathutils import Vector, Quaternion

DURATIONS = {'Idle': 60, 'Walk': 36, 'Run': 24, 'Windup': 24, 'Strike': 35, 'Hit': 15, 'Death': 42}
IMPACT = .14


def smooth(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


def envelope(t, keys):
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if t <= b:
            f = smooth((t - a) / (b - a))
            return va + (vb - va) * f
    return keys[-1][1]


def set_pose(rig, kind, t):
    for bone in rig.pose.bones:
        bone.rotation_mode = 'QUATERNION'
        bone.rotation_quaternion = Quaternion()
        bone.location = (0, 0, 0)

    def turn(name, axis, degrees):
        bone = rig.pose.bones[name]
        local_axis = bone.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
        bone.rotation_quaternion @= Quaternion(local_axis, math.radians(degrees))

    def arm(side, drop, forward, bend):
        sign = 1 if side == 'L' else -1
        turn('UpperArm.' + side, (0, 1, 0), sign * drop)
        turn('UpperArm.' + side, (1, 0, 0), forward)
        turn('Forearm.' + side, (0, 0, 1), -sign * bend)

    def leg(side, y, lift, hip_height):
        # Knee bends toward the character's front, ankle counter-rotates to keep the sole level.
        upper = .43
        lower = .41
        vertical = hip_height - (.13 + lift)
        distance = min(upper + lower - .001, math.hypot(y, vertical))
        aim = math.atan2(y, vertical)
        opening = math.acos(max(-1, min(1, (upper * upper + distance * distance - lower * lower) / (2 * upper * distance))))
        thigh = aim - opening
        knee = math.pi - math.acos(max(-1, min(1, (upper * upper + lower * lower - distance * distance) / (2 * upper * lower))))
        turn('Thigh.' + side, (1, 0, 0), math.degrees(thigh))
        turn('Shin.' + side, (1, 0, 0), math.degrees(knee))
        turn('Foot.' + side, (1, 0, 0), -math.degrees(thigh + knee))

    arm('L', 63, -8, 22)
    arm('R', 62, 2, 16)
    hip_height = .95
    feet = {'L': (-.06, 0), 'R': (.06, 0)}

    if kind == 'Idle':
        breath = math.sin(t * math.tau)
        turn('Spine', (1, 0, 0), breath * .65)
        turn('Chest', (1, 0, 0), breath * 1.15)
        turn('Head', (0, 0, 1), math.sin(t * math.tau) * 1.4)
        turn('Clavicle.L', (0, 1, 0), breath * .6)
        turn('Clavicle.R', (0, 1, 0), -breath * .6)
    elif kind in ('Walk', 'Run'):
        run = kind == 'Run'
        stance, span, height = (.5, .70, .12) if run else (.6, .55, .065)
        hip_height = (.885 if run else .92) + (.006 if run else .003) * math.cos(t * math.tau * 2)
        for side, offset in [('L', 0), ('R', .5)]:
            phase = (t + offset) % 1
            if phase < stance:
                feet[side] = (-span / 2 + span * phase / stance, 0)
            else:
                swing = (phase - stance) / (1 - stance)
                feet[side] = (span / 2 - span * smooth(swing), height * math.sin(swing * math.pi) ** 2)
            # Counter-swing remains restrained on the sword arm; clavicles absorb the step.
            wave = math.cos((t + offset) * math.tau)
            turn('UpperArm.' + side, (1, 0, 0), wave * (13 if run else 7) * (1 if side == 'L' else .55))
            turn('Clavicle.' + side, (1, 0, 0), wave * 1.5)
        turn('Chest', (0, 0, 1), math.sin(t * math.tau) * (4 if run else 2.5))
        turn('Chest', (1, 0, 0), 7 if run else 2)
        turn('Head', (1, 0, 0), -4 if run else -1)
    elif kind in ('Windup', 'Strike'):
        if kind == 'Windup':
            brace = smooth(t)
            raise_arm, twist, elbow, chest, head = [v * brace for v in (80, 32, 50, -22, 12)]
        else:
            brace = 1 - smooth((t - .48) / .52)
            start = (80, 32, 50, -22, 12)
            impact = (-5, -58, 5, 22, -8)
            follow = (-18, -70, 0, 28, -10)
            values = [envelope(t, [(0, a), (IMPACT, b), (.30, c), (.42, c), (1, 0)])
                      for a, b, c in zip(start, impact, follow)]
            raise_arm, twist, elbow, chest, head = values
        hip_height -= .025 * brace
        feet = {'L': (-.06 - .12 * brace, 0), 'R': (.06 + .10 * brace, 0)}
        turn('UpperArm.R', (0, 1, 0), raise_arm)
        turn('UpperArm.R', (0, 0, 1), twist)
        turn('Forearm.R', (0, 0, 1), elbow)
        turn('Clavicle.R', (0, 0, 1), chest * .12)
        turn('Spine', (0, 0, 1), chest * .25)
        turn('Chest', (0, 0, 1), chest * .75)
        turn('Head', (0, 0, 1), head)
        turn('UpperArm.L', (1, 0, 0), -10 * brace)
    elif kind == 'Hit':
        recoil = envelope(t, [(0, 0), (.2, 1), (.7, -.08), (1, 0)])
        turn('Spine', (1, 0, 0), -5 * recoil)
        turn('Chest', (1, 0, 0), -12 * recoil)
        turn('Head', (1, 0, 0), -9 * envelope(t, [(0, 0), (.3, 1), (1, 0)]))
        turn('UpperArm.R', (1, 0, 0), -8 * recoil)
        hip_height -= .035 * max(0, recoil)
    elif kind == 'Death':
        buckle = envelope(t, [(0, 0), (.3, 1), (1, .2)])
        fall = smooth((t - .18) / .82)
        hip_height -= .14 * buckle
        turn('Root', (1, 0, 0), -86 * fall)
        rig.pose.bones['Root'].location.y = .13 * fall
        turn('Chest', (1, 0, 0), 12 * buckle)
        turn('Head', (1, 0, 0), 10 * buckle)
        turn('UpperArm.L', (0, 1, 0), -22 * fall)
        turn('UpperArm.R', (0, 1, 0), 15 * fall)

    rig.pose.bones['Hips'].location.y = hip_height - .97
    for side, (y, lift) in feet.items():
        leg(side, y, lift, hip_height)
