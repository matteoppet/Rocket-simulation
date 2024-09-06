# Terrain algorithm (this readme is temporary, will be updated later)
The terrain consinsts on a stack of 3 sprites, each sprite has the same size, same color, but different position and different id.<br/>
The terrains are this: -> [Terrain_id0, Terrain_id1, Terrain_id2]<br/>

The rocket is created at the center of the terrain id=1, if the rocket center position is grater than the terrain id=1's centerx position, the terrain with id=0 will be eliminated<br/>
and it will be created and added to the group a terrain with id=2 and all other terrain remained in the group, each id will be shifted by -1. <br/>

### Example
1. Initialization stack -> [Terrain_id0, Terrain_id1, Terrain_id2]<br/>
2. rocket postiion -> is moving to the right<br/>
3. Stack elimination terrain_id0 -> [Terrain_id1, Terrain_id2]<br/>
4. Shift the ids of each terrain by -1 -> [Terrain_id0, Terrain_id1]<br/>
5. Add the third terrain with the new position -> [Terrain_id0, Terrain_id1, Terrain_id2]<br/>