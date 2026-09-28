# Transferable lessons from mammals

Mammal work shows two things clearly: direct tracking is precise but covers few individuals, and designed surveys with explicit detection models produce the population estimates.

## What these systems do

- **GPS collars** give accurate tracks for animals large enough to carry them (Tomkiewicz et al. 2010, S19). Tag mass limits remain a real constraint (Portugal and White 2018, S17), and tags can change behavior, as shown for birds (Barron et al. 2010, S18).
- **Camera traps** support occupancy and density estimates when linked to a sampling design (Burton et al. 2015, S26). Density can be estimated without individual recognition from encounter rates, detection zones, and speed (Rowcliffe et al. 2008, S28). Automated image classifiers must be validated (Norouzzadeh et al. 2018, S27).
- **Spatial capture-recapture** estimates density when individuals can be identified at detectors (Royle et al. 2014, S46).
- **Bat acoustic monitoring** in North America is organized around a grid-based sampling frame (Loeb et al. 2015, S112).
- **Marine mammals** are estimated from designed aerial and ship surveys (Hammond et al. 2013, S49) and habitat-based density models built on them (Roberts et al. 2016, S51; WhaleWatch, Hazen et al. 2017, S76).
- **Near real-time whale acoustics.** A moored buoy reported daily occurrence of four baleen whale species with 0 percent false detections for right, humpback, and sei whales and 12 to 42 percent daily missed detections. Right whale detections matched aerial sightings within about 30 to 40 km over 24 to 48 hours; humpback detections showed no association with sightings (Baumgartner et al. 2019, S31; checked this pass).
- **Satellite imagery** can count whales at the surface (Fretwell et al. 2014, S25).
- **Tracking data can be misused** to find and harm animals (Cooke et al. 2017, S84).

## What transfers to FishAI

1. **Design the sampling frame first.** A grid or stratified random design makes later inference possible. Reef Visual Census already follows this pattern.
2. **Separate detection from density.** Distance sampling, encounter-rate methods, and capture-recapture all model how likely an animal is to be seen.
3. **A sensor's meaning can differ by species inside one system.** The whale buoy worked for right whales and not for humpbacks. Every species-sensor pair needs its own validation.
4. **Density surfaces built on designed surveys plus habitat are the closest template** to what FishAI wants at Level 2.
5. **Individual tracking is most valuable for parameters,** such as movement rates and residency, that inform population models.
6. **Automated classifiers must report error rates** before their output becomes evidence.

## What does not transfer

- GPS and cellular tags do not work underwater.
- Aerial counts see very few fish.

## FishAI actions

- Keep species-specific validation for every future sensor.
- Use designed surveys, not opportunistic reports, as the backbone of any density surface.
- Treat tag data as a way to estimate movement parameters, never as a public map.
