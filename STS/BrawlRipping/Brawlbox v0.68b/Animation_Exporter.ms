---------------------------------------------------------------------------
-- *** KEYFRAME EXPORTER ***
---------------------------------------------------------------------------
-- Keyframe Data Export to Brawlbox
-- based on Keyframe Exporter 0.95 by Tonio Freitag (www.toniofreitag.com)
-- based on AE Position Exporter by Aaron Dabelow (www.aarondabelow.com)
--
-- written by eXiggah (www.brawlismagic.blogspot.com)
---------------------------------------------------------------------------
-- exports Animated or Static Keyframes to Brawlbox
---------------------------------------------------------------------------

try(destroyDialog AEKeyframeExporter)catch(print "buck")
(
	(-------------------- VARIABLE SETUP--------------------
	local xPosAE
	local yPosAE
	local zPosAE
	local xRotAE
	local yRotAE
	local zRotAE
	local xSclAE
	local ySclAE
	local zSclAE
	local timerange = #range
	local frame = 0
	local framestart = 0
	local frameend = 0
	local thehelper
	local FKHelper
	local thechain
	local targetbone
	local objAll
	local hasChanged = "000000000"
	local lastValue = ""
	local PositionX = ""
	local PositionY = ""
	local PositionZ = ""
	local OrientationX = ""
	local OrientationY = ""
	local OrientationZ = ""
	local ScaleX = ""
	local ScaleY = ""
	local ScaleZ = ""
	----------------------STRING SETUP------------------------
	local headerText = "Animation Keyframe Data"
	local setupText = "\n\t\nKeyframe Data \nBonen"
	local positionText = "\n\t\nTranslation"
	local orientationText = "\n\t\nRotation"
	local scaleText = "\n\t\nScale"
	local xText = "\n\t\nX"
	local yText = "\n\t\nY"
	local zText = "\n\t\nZ"
	local footerText = "\n\t\nEnd of Keyframe Data"
	local positionData = stringStream ""
	local orientationData = stringStream ""
	local scaleData = stringStream ""
	local dataText = stringStream ""
	)
	----------------------FUNCTIONS------------------------
	function getCurrentData theObject=
	(		
		if frame == framestart then
		(
			XPosAE = (formattedprint theObject.inode.posInParent.x format:".5f") as string
			YPosAE = (formattedprint theObject.inode.posInParent.y format:".5f") as string
			ZPosAE = (formattedprint theObject.inode.posInParent.z format:".5f") as string
			XRotAE = (formattedprint theObject.inode.rotInParent.x format:".5f") as string
			YRotAE = (formattedprint theObject.inode.rotInParent.y format:".5f") as string
			ZRotAE = (formattedprint theObject.inode.rotInParent.z format:".5f") as string
			XSclAE = (formattedprint theObject.inode.scaleInParent.x format:".5f") as string
			YSclAE = (formattedprint theObject.inode.scaleInParent.y format:".5f") as string
			ZSclAE = (formattedprint theObject.inode.scaleInParent.z format:".5f") as string
			
			if XPosAE == "-0.00000" then
				(XPosAE = "0.00000")
			if YPosAE == "-0.00000" then
				(YPosAE = "0.00000")
			if ZPosAE == "-0.00000" then
				(ZPosAE = "0.00000")
			if XRotAE == "-0.00000" then
				(XRotAE = "0.00000")
			if YRotAE == "-0.00000" then
				(YRotAE = "0.00000")
			if ZRotAE == "-0.00000" then
				(ZRotAE = "0.00000")
			if XSclAE == "-0.00000" then
				(XSclAE = "0.00000")
			if YSclAE == "-0.00000" then
				(YSclAE = "0.00000")
			if ZSclAE == "-0.00000" then
				(ZSclAE = "0.00000")
		)
		else
		(
			( --Position Values
			lastValue = XPosAE
			XPosAE = (formattedprint theObject.inode.posInParent.x format:".5f") as string
			if XPosAE == "-0.00000" then
				(XPosAE = "0.00000")
			if XPosAE != lastValue and (XPosAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 1 1 "1")
			
			lastValue = YPosAE
			YPosAE = (formattedprint theObject.inode.posInParent.y format:".5f") as string
			if YPosAE == "-0.00000" then
				(YPosAE = "0.00000")
			if YPosAE != lastValue and (YPosAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 2 1 "1")
			
			lastValue = ZPosAE
			ZPosAE = (formattedprint theObject.inode.posInParent.z format:".5f") as string
				if ZPosAE == "-0.00000" then
				(ZPosAE = "0.00000")
			if ZPosAE != lastValue and (ZPosAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 3 1 "1")
			)
			
			( --Rotation Values
			lastValue = XRotAE
			XRotAE = (formattedprint theObject.inode.rotInParent.x format:".5f") as string
			if XRotAE == "-0.00000" then
				(XRotAE = "0.00000")
			if XRotAE != lastValue and (XRotAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 4 1 "1")
			
			lastValue = YRotAE
			YRotAE = (formattedprint theObject.inode.rotInParent.y format:".5f") as string
			if YRotAE == "-0.00000" then
				(YRotAE = "0.00000")
			if YRotAE != lastValue and (YRotAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 5 1 "1")
			
			lastValue = ZRotAE
			ZRotAE = (formattedprint theObject.inode.rotInParent.z format:".5f") as string
			if ZRotAE == "-0.00000" then
				(ZRotAE = "0.00000")
			if ZRotAE != lastValue and (ZRotAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 6 1 "1")
			)
			
			( --Scale Values
			lastValue = XSclAE
			XSclAE = (formattedprint theObject.inode.scaleInParent.x format:".5f") as string
			if XSclAE == "-0.00000" then
				(XSclAE = "0.00000")
			if XSclAE != lastValue and (XSclAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 7 1 "1")
				lastValue = YSclAE
			YSclAE = (formattedprint theObject.inode.scaleInParent.y format:".5f") as string
			if YSclAE == "-0.00000" then
				(YSclAE = "0.00000")
			if YSclAE != lastValue and (YSclAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 8 1 "1")
			
			lastValue = ZSclAE
			ZSclAE = (formattedprint theObject.inode.scaleInParent.z format:".5f") as string
			if ZSclAE == "-0.00000" then
				(ZSclAE = "0.00000")
			if ZSclAE != lastValue and (ZSclAE as float - lastValue as float) > 0.001 then
				(hasChanged = replace hasChanged 9 1 "1")
			)
		)
		
		frame += 1
	
		( -- Update Values
		PositionX += "\n" + XPosAE
		PositionY += "\n" + YPosAE
		PositionZ += "\n" + ZPosAE
		OrientationX += "\n" + XRotAE
		OrientationY += "\n" + YRotAE
		OrientationZ += "\n" + ZRotAE
		ScaleX += "\n" + XSclAE
		ScaleY += "\n" + YSclAE
		ScaleZ += "\n" + ZSclAE
		)
		
	)

	function collectData status bonen=
	(	
		PositionX = ""
		PositionY = ""
		PositionZ = ""
		OrientationX = ""
		OrientationY = ""
		OrientationZ = ""
		ScaleX = ""
		ScaleY = ""
		ScaleZ = ""
		hasChanged = "000000000"
		frame = framestart
		
		positionData = stringStream ""
		orientationData = stringStream ""
		scaleData = stringStream ""
		
		disableSceneRedraw()
		status.text = "collecting data..."
		now = sliderTime
		
		for f = framestart to frameend do
		(				
			sliderTime = f
			if (substring bonen.name 1 4) != "null" then
			(	getCurrentData bonen	)
		)
		
		sliderTime = framestart
		
		( --Updates only changed values
			( --Position
				format "%" positionText to:positionData
				if (substring hasChanged 1 1 as number) == 1 then
				(
					format "%" xText to:positionData
					format "%" PositionX to:positionData
				)
				else if bonen.inode.posInParent.x > 0.001 or bonen.inode.posInParent.x < -0.001 then
				(	format "%" xText to:positionData
					PositionX = "\n" + (formattedprint bonen.inode.posInParent.x format:".5f") as string
					format "%" PositionX to:positionData
				)
				
				if (substring hasChanged 2 1 as number) == 1 then
				(
					format "%" yText to:positionData
					format "%" PositionY to:positionData
				)
				else if bonen.inode.posInParent.y > 0.001 or bonen.inode.posInParent.y < -0.001 then
				(	format "%" yText to:positionData
					PositionY = "\n" + (formattedprint bonen.inode.posInParent.y format:".5f") as string
					format "%" PositionY to:positionData
				)
				
				if (substring hasChanged 3 1 as number) == 1 then
				(
					format "%" zText to:positionData
					format "%" PositionZ to:positionData
				)
				else if bonen.inode.posInParent.z > 0.001 or bonen.inode.posInParent.z < -0.001 then
				(	format "%" zText to:positionData
					PositionZ = "\n" + (formattedprint bonen.inode.posInParent.z format:".5f") as string
					format "%" PositionZ to:positionData
				)
			)
			
			( --Rotation
				format "%" orientationText to:orientationData
				if (substring hasChanged 4 1 as number) == 1 then
				(
					format "%" xText to:orientationData
					format "%" OrientationX to:orientationData
				)
				else if bonen.inode.rotInParent.x > 0.001 or bonen.inode.rotInParent.x < -0.001 then
				(	format "%" xText to:orientationData
					OrientationX = "\n" + (formattedprint bonen.inode.rotInParent.x format:".5f") as string
					format "%" OrientationX to:orientationData
				)
				
				if (substring hasChanged 5 1 as number) == 1 then
				(
					format "%" yText to:orientationData
					format "%" OrientationY to:orientationData
				)
				else if bonen.inode.rotInParent.y > 0.001 or bonen.inode.rotInParent.y < -0.001 then
				(	format "%" yText to:orientationData
					OrientationY = "\n" + (formattedprint bonen.inode.rotInParent.y format:".5f") as string
					format "%" OrientationY to:orientationData
				)
				
				if (substring hasChanged 6 1 as number) == 1 then
				(
					format "%" zText to:orientationData
					format "%" OrientationZ to:orientationData
				)
				else if bonen.inode.rotInParent.z > 0.001 or bonen.inode.rotInParent.z < -0.001 then
				(	format "%" zText to:orientationData
					OrientationZ = "\n" + (formattedprint bonen.inode.rotInParent.z format:".5f") as string
					format "%" OrientationZ to:orientationData
				)
			)
			
			if (substring hasChanged 7 3 as number) > 0 then
			( --Scale
				format "%" scaleText to:scaleData
				if (substring hasChanged 7 1 as number) == 1 then
				(
					format "%" xText to:scaleData
					format "%" ScaleX to:scaleData
				)
				if (substring hasChanged 8 1 as number) == 1 then
				(
					format "%" yText to:scaleData
					format "%" ScaleY to:scaleData
				)
				if (substring hasChanged 9 1 as number) == 1 then
				(
					format "%" zText to:scaleData
					format "%" ScaleZ to:scaleData
				)
			)
		)
			
			sliderTime = now
			
		if (hasChanged as float) != 0 then
		(
			setupText = "\n\t\nKeyframe Data\n" + bonen.name
			format "%" setupText to:dataText
			format "%" (positionData as string) to:dataText
			format "%" (orientationData as string) to:dataText
			format "%" (scaleData as string) to:dataText
			format "%" footerText to:dataText
		)
		
		( --AE Reset
		xPosAE = ""
		yPosAE = ""
		zPosAE = ""
		xRotAE = ""
		yRotAE = ""
		zRotAE = ""
		xSclAE = ""
		ySclAE = ""
		zSclAE = ""
		)
		
		enableSceneRedraw()
	)

	----------------DEFINE ROLLOUT------------------
	rollout AEKeyframeExporter "Brawl Animation Export" width:200
	(
		group "Object Selection"
		(
			button bSelectAll width: 175 height:20
			radiobuttons bSelectType labels:#("Models", "Bones", "Helpers") columns: 3
		)
		
		group "Export Options"
		(
			radiobuttons bSwitch labels:#("All Frames", "Specified") columns:2
			button bSaveData "Bake Animation" width:150 height:20 enabled:false
			spinner frameFirst "First Frame" range:[0, 100000, 0] type:#integer
			spinner frameSecond "Second Frame" range:[0,100000, 1] type:#integer
		)
		
		group "Status"
		(
			label lStatus ""
			progressbar prog
			label lCam ""
		)
		
		group "Actions"
		(
			dropdownlist dAction items:#("Align FK/IK Helper", "Reset Selected", "Resize bones", "test")
			button bAction "Perform Selected Option" width:150 height:20
			button bAction2 "---" width:150 height:20
		)
		----------------   ROLLOUT ACTIONS   ------------------
		on AEKeyframeExporter open do
		(
			--if $ != null and selection.count == 1 and $.name == "TopN" then
				bSelectAll.caption = "Select All Bones"
				bSelectType.state = 2
				lStatus.text = "Click Select All to select Bones"
				if superclassof $ == camera do
				(
					lCam.text = "Angle Of View: " + ($.fov as string) + "turn off Auto Orientation!"
				)
		)
		
		on bSelectAll pressed do
		(
			if bSelectType.state == 1 then --Select All Models
			(
				select geometry
				for obj in (selection as array) do
					if obj.baseObject as string != "Editable Mesh" and obj.baseObject as string != "Editable Poly" then 
					(deselect obj)
				bSaveData.enabled = false
				bSelectAll.caption = "All Models Selected"
				lStatus.text = "Click Select All to select Bones"
			)
			
			if bSelectType.state == 2 then --Select All Bones
			(
				obj = $TopN
				objAll = $TopN...*
				select objAll
				bSaveData.enabled = true
				bSelectAll.caption = "All Bones Selected" +  " (" + (objAll.count as string) + ")"
				lStatus.text = "Choose Export Option"
				prog.color = blue
			)
			
			if bSelectType.state == 3 then --Select All Helpers
			(
				select helpers
				select shapes
				objAll = $TopN...*
				deselect objAll
				bSaveData.enabled = false
				bSaveData.enabled = false
				bSelectAll.caption = "All Helpers Selected"
				lStatus.text = "Click Select All to select Bones"
			)
			
			if bSelectType.state == 4 then --Select All Chains
			(
				objAll = $IKChain*
				select objAll
				objAll = $FKChain*
				select objAll
				bSaveData.enabled = false
				bSaveData.enabled = false
				bSelectAll.caption = "All Chains Selected"
				lStatus.text = "Click Select All to select Bones"
			)
		)
		
		on BSelectType changed state do
		(
			bSelectType.state = state
			
			if bSelectType.state == 1 then --Select Models
			(
				bSelectAll.caption = "Select All Models"
			)
			
			if bSelectType.state == 2 then --Select Bones
			(
				bSelectAll.caption = "Select All Bones"
			)
			
			if bSelectType.state == 3 then --Select Helpers
			(
				bSelectAll.caption = "Select All Helpers"
			)
		)
		
		on bSwitch changed state do
		(
			bSwitch.state = state
		)
		
		on bSaveData pressed do
		(
			if selection.count == objAll.count then
			(
				try
				(
					saveForAEFileStaticName = GetSaveFileName filename:(MaxFilePath + "animation.txt") types:"text(*.txt)"
					if saveForAEFileStaticName != undefined then
					(
						saveForAEFileStatic = createfile saveForAEFileStaticName
						
						if bSwitch.state == 2 or frameSecond.value != 1 then
						(
							framestart = frameFirst.value
							frameend = frameSecond.value
						)
						else if bSwitch.state == 1 then 
						(
							framestart = animationrange.start
							frameend = animationrange.end
						)
						
						headerText = headerText + " Frames\n" + ((frameend - framestart + 1) as string)
						format "%" headerText to:dataText
						headerText = "Animation Keyframe Data"
						
						for i = 2 to objAll.count Do
						(
							collectData lStatus objAll[i]
							lStatus.text = "formatting data..."
							format "%" (dataText as String) to:saveForAEFileStatic
							dataText = stringStream ""
							prog.value = (100 / objAll.count) * (i + 5)
						)
						
						format "%" "\n\t\nEnd of Animation Data" to:saveforAEFileStatic
						for i = 5 to 54 Do
							(format "%" "\n" to:saveforAEFileStatic)
						enableSceneRedraw()
						close saveForAEFileStatic
						lStatus.text = "Saved to file!"
						prog.value = 100
						prog.color = green
					)
					else (messageBox "Click the top button to select Root Bone" title:"TopN Not Selected")
				)
				catch
				( 
					enableSceneRedraw()
					(Messagebox "Error")
				)
			)
			else (messageBox "Click the top button to select Root Bone" title:"TopN Not Selected")
		)
		
		on bAction pressed do
		(
			if dAction.selection == 1 then --Match FK/IK Helpers
			(
				helpername = substring $.name 1 8 as string
				
				if helpername == "IKHelper"  and selection.count == 1 then --IKHelper
				(
					thehelper = selection[1]					
					chainname = "IKChain_lolol" + (substring $.name 10 -1 as string)
					FKname = "FKHelper_" +  (substring $.name 10 -1 as string)
					FKhelper = Execute ("$'"+FKname+"'")
					thechain = Execute ("$'"+chainname+"'")
					if thechain == undefined then (messagebox("lol"))
					targetbone = thechain.transform.controller.endJoint
					
					if thechain.inode.rotInParent.x  == targetbone.inode.posInParent.x then
					(
						messagebox("No Action.")
					)
					
					FKHelper.parent = null
					thechain.parent = null
					select thechain
					IKChainControl.toggleEnabled()
					IKChainControl.toggleEnabled()
					deselect thechain
					
					in coordsys world
					(
						thehelper.inode.posInParent = thechaininode.posInParent
						thehelper.inode.scaleInParent = targetbone.inode.scaleInParent
					)
					
					thechain.parent = thehelper
					FKHelper.parent = thehelper
					select thehelper
				)
				else if helpername == "FKHelper"  and selection.count == 1 then --FKHelper
				(
					thehelper = selection[1]					
					chainname = "FKChain_" + (substring $.name 10 -1 as string)
					thechain = Execute ("$'"+chainname+"'")
					targetbone = thechain.transform.controller.endJoint
					
					in coordsys world
					(
						thehelperinode.posInParent = targetbone.inode.posInParent
					)
					
					select thehelper
				)
				else (messagebox "Please select one helper.")
			)
			
			if dAction.selection == 2 then --Reset Selected
			(
				macros.run "Animation Tools" "TransformToZero"
			)

			if dAction.selection == 3 then --Resize Bones
			(
				if selection.count == objAll.count then
					(
						try
						(
							lStatus.text = "Resizing bones..."
							for i = 2 to objAll.count Do
							(
								objAll[i].width = 0.5
								objAll[i].height = 0.5
								prog.value = (100 / objAll.count) * (i + 5)
							)
							lStatus.text = "Finished resizing!"
							prog.value = 100
							prog.color = green
						)
						catch(Messagebox "Error")
					)
				else (messagebox "Please select all bones.")
			)
			
			if dAction.selection == 4 then --Maxscript Position Test
			(
				--messagebox("Position Values, innaccurate world " + $.pos.controller.value as string + " Accurate parent " + $.controller.value.pos as string)
				--messagebox("Rotation Values, world " + quattoeuler($.rotation.controller.value) as string + " or parent " + quattoeuler($.controller.value.rotation) as string)
				--messagebox("Scale Values, world " + $.scale.controller.value as string + " or parent " + $.controller.value.scale as string)
				
				messagebox("New Test, " + $.inode.rotInParent.x as string + ", " + $.inode.rotInParent.y as string + ", " + $.inode.rotInParent.z as string)
			)
		)
		
		on bAction2 pressed do
		(
			if bAction2.text == "---" then ()
		)
	)
	--------------ROLLOUT CONSTRUCTION---------------
	createDialog AEKeyframeExporter
)