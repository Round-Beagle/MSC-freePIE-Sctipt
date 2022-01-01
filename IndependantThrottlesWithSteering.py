	# =============================================================================================
	# /////////////////////////////////////// My Summer Car ///////////////////////////////////////
	# =============================================================================================
	# This is a modified script, the original script was written by Skagen 
	# url: https://www.lfs.net/forum/post/1862759#post1862759
	# Additional modification work by jds711
	# url: https://www.youtube.com/watch?v=DaTrJvhTz3w
	# This version by Randox
	# url: http://steamcommunity.com/sharedfiles/filedetails/?id=936937766
	# =============================================================================================
	# This script will use only Y axis by default
	# 1. Steering (X-Axis)
	# 2. Throttle (Y-Axis)
	# 3. Brake (Z-Axis)
	# =============================================================================================
	# Use vJoy Feeder to set the axis in launcher
	# =============================================================================================
"""This script is an experimental version of the script that has been turned for My Summer Car
	by Randox. It features the original independant brake and throttle axis rather than combined.
	This script maps the throttle and brake buttons to a vjoy controller axis, and adds a slight
	attack and release time to both the accelerator and break for slightly smother operation. It
	also includes a secondary mode, which lowers the maximum throttle and break value (for easy
	driving and more controlled braking), and a hold mode which causes throttle and brake to apply
	and release more slowly (intended for smoother tap driving, when trying to hold a certain speed).
	When hold mode is on, the secondary toggle will cycle through an extra third mode which further
	lowers the maximum throttle value (but not gas).
	
	There are 3 extra keybinds to control these functions. One each for the secondary toggle, hold
	toggle, and a reset button that turns the other two off. The space bar will also disable
	secondary, low, and hold modes by default.
	
	I've also included the necessary code for mouse steering. The code I used can be
	in the description of the youtube video linked above. All the code here was pulled from the
	F1 2014 scripts, or written by me.

	Please feel free to edit this code as you see fit. If you redistribute it, please include credit
	to myself, jds711, and Skagen."""
if starting:
	system.setThreadTiming(TimingTypes.HighresSystemTimer)
	system.threadExecutionInterval = 5
	def calculate_rate(max, time):
		if time > 0:
			return max / (time / system.threadExecutionInterval)
		else:
			return max
	# These were +1 and -1 in source material.
	# You MUST use +/- 2 for My Summer Car or axis may spontaneously invert
	int32_max = (2 ** 14) - 2
	int32_min = (( 2 ** 14) * -1) + 2
	
	v = vJoy[0]
	v.x, v.y, v.z, v.rx, v.ry, v.rz, v.slider, v.dial = (int32_min,) * 8
	# =============================================================================================
	# //////////////////////////////////////// SETTINGS ///////////////////////////////////////////
	# =============================================================================================
	# Mouse settings
	# =============================================================================================
	# Higher SCR = Smoother/Slower Response | Lower SCR = Harder/Quicker Response
	# With the game's built in steering settings, there's no need to change the scr value
	# SCR's effects can be felt better with arcade style racing games
	global mouse_sensitivity, sensitivity_center_reduction
	mouse_sensitivity = 15
	sensitivity_center_reduction = 0.9
	# =============================================================================================
	# Steering settings
	# =============================================================================================
	global steering, steering_max, steering_min, steering_center_reduction	
	# Init values, do not change
	steering = 0.0
	steering_max = float(int32_max)
	steering_min = float(int32_min)
	steering_center_reduction = 1.0
	# =============================================================================================
	# Throttle, Break, and Control Keys:
	# =============================================================================================
	global throttle_key, throttle_key_sec, throttle_key_ter, brake_key, throttle_key_hold, reset_key
	global space_reset_enabled, low_mode_enabled, steering_key_pause
	throttle_key = Key.W
	throttle_key_sec = Key.T
	brake_key = Key.S
	throttle_key_hold = Key.Y
	reset_key = Key.U
	steering_key_pause = Key.B
	#Change "True" to "False" to disable Space Bar as reset and low mode respecitvely
	space_reset_enabled = True
	low_mode_enabled = True
	# =============================================================================================
	# Throttle settings
	# =============================================================================================
	# Set throttle behaviour with the increase and decrease time (ms)
	# the actual increase and decrease rates are calculated automatically
	throttle_increase_time = 160
	throttle_decrease_time = 200
	# global declarations
	global throttle, throttle_max, throttle_min, throttle_increase_rate, throttle_decrease_rate
	global throttle_sec, throttle_low
	global throttle_sec_set, throttle_hold_set, throttle_inc_mod, throttle_dec_mod, throttle_low_set
	global braking_sec
	#initialization values. Do not change.
	throttle_max = int32_max
	throttle_min = int32_min
	throttle_increase_rate = calculate_rate(throttle_max, throttle_increase_time)
	throttle_decrease_rate = calculate_rate(throttle_max, throttle_decrease_time) * -1
	throttle_sec_set = False
	throttle_hold_set = False
	throttle_low_set = False	
	throttle = throttle_min
	#additional setup parameters
	# _sec and _low modifiers are used to lower maximum values
	# _mod values are for alternate attack and release rates
	throttle_sec = 0.63 * int32_max
	throttle_low = 0.4 * int32_max
	braking_sec = 0.5 * int32_max
	throttle_inc_mod = 0.25
	throttle_dec_mod = 0.15	
	# =============================================================================================
	# Braking settings
	# =============================================================================================
	# Set throttle behaviour with the increase and decrease time (ms)
	# the actual increase and decrease rates are calculated automatically
	braking_increase_time = 160
	braking_decrease_time = 100
	# Init values, do not change
	global braking, braking_max, braking_min, braking_increase_rate
	global braking_decrease_rate, braking_sec
	braking_max = int32_max
	braking_min = int32_min
	braking = braking_min
	braking_increase_rate = calculate_rate(braking_max, braking_increase_time)
	braking_decrease_rate = calculate_rate(braking_max, braking_decrease_time) * -1  
# =================================================================================================
# LOOP START
# =================================================================================================
# Logic Toggles
# =================================================================================================
"""The Secondary toggle applies reduced maximum values for positive and negative Y Axis
independantly for more gentle acceleration and braking. The Hold toggle applies lower attack and
release rates, to aid in tap acceleration/braking.
When Hold mode is on, there is an additonal Low mode for throttle only for an even lower maximum,
and the secondary toggle will progress through the 3 maximums sequentially. Turning off the hold
toggle also disables the low mode.

Reset toggle sets everything back for normal operation. The space bar (handbrake by default) can
also be used as a reset key (enabled by default)"""
if keyboard.getPressed(throttle_key_sec):
	if throttle_sec_set == False:
		throttle_sec_set = True
	elif throttle_sec_set == True and throttle_hold_set == True and low_mode_enabled == True:
		if throttle_low_set == False:
			throttle_low_set = True
		else:
			throttle_low_set = False
			throttle_sec_set = False
	else:
		throttle_sec_set = False
		throttle_low_set = False
if keyboard.getPressed(throttle_key_hold):
	if throttle_hold_set == False:
		throttle_hold_set = True
	else:
		throttle_hold_set = False
		throttle_low_set = False
if keyboard.getKeyDown(reset_key):
	throttle_hold_set = False
	throttle_sec_set = False
	throttle_low_set = False
if keyboard.getKeyDown(Key.Space) and space_reset_enabled == True:
	throttle_hold_set = False
	throttle_sec_set = False
	throttle_low_set = False
# =================================================================================================
# Throttle logic
# =================================================================================================
#if throttle down, increase throttle, else decrease throttle
if keyboard.getKeyDown(throttle_key):
	if throttle_hold_set == True:
		throttle = throttle + (throttle_increase_rate * throttle_inc_mod)
	else:
		throttle = throttle + throttle_increase_rate
else:
	if throttle_hold_set == True:
		throttle = throttle + (throttle_decrease_rate * throttle_dec_mod)
	else:
		throttle = throttle + throttle_decrease_rate
#Apply alternate maximum axis values for secondary and low toggles, and cap output to axis maximums
if throttle > throttle_low and throttle_low_set == True:
	throttle = throttle_low
elif throttle > throttle_sec and throttle_sec_set == True:
	throttle = throttle_sec
elif throttle > throttle_max:
	throttle = throttle_max
elif throttle < throttle_min:
	throttle = throttle_min
v.y = throttle
# =================================================================================================
# Braking logic
# =================================================================================================
if keyboard.getKeyDown(brake_key):
	if throttle_hold_set == True:
		braking = braking + (braking_increase_rate * throttle_inc_mod)
	else:
		braking = braking + braking_increase_rate
else:
	if throttle_hold_set == True:
		braking = braking + (braking_decrease_rate * throttle_inc_mod)
	else:
		braking = braking + braking_decrease_rate
#Apply alternate maximum axis values for secondary and low toggles, and cap output to axis maximums
if braking > braking_sec and throttle_sec_set == True:
	braking = braking_sec
elif braking > braking_max:
	braking = braking_max
elif braking < braking_min:
	braking = braking_min
v.z = braking
# =================================================================================================
# Steering logic
# =================================================================================================
if mouse.wheelUp:
	steering = 0.0
if steering > 0:
	steering_center_reduction = sensitivity_center_reduction ** (1 - (steering / steering_max))
elif steering < 0:
	steering_center_reduction = sensitivity_center_reduction ** (1 - (steering / steering_min))
if keyboard.getKeyUp(steering_key_pause):
	steering = steering + ((float(mouse.deltaX) * mouse_sensitivity) / steering_center_reduction)
if steering > steering_max:
	steering = steering_max
elif steering < steering_min:
	steering = steering_min
v.x = int(round(steering))
# =================================================================================================
# vJoy BUTTONS 
# F1 2014 allows keyboard controls mixed with other input devices, so we don't need to set any more
# =================================================================================================
v.setButton(0,int(mouse.leftButton))
v.setButton(1,int(mouse.rightButton))
v.setButton(2,int(mouse.middleButton))
# =================================================================================================
# PIE diagnostics logic
# =================================================================================================
diagnostics.watch(v.y)
diagnostics.watch(v.z)
diagnostics.watch(throttle_hold_set)
diagnostics.watch(throttle_sec_set)
diagnostics.watch(throttle_low_set)
diagnostics.watch(v.x) #diagnostic output if steering is enabled