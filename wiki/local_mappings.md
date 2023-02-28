## Local mapping of programs

Since sometimes Miele API is reporting different programs for the same numeric program id and appliance category, the program name reported by program sensor of this integration could be wrong. For this reason, it is possible to specify in configuration.yaml a local mapping, in order to provide the correct program names of your appliance. For example, for tumble dryers such as TCJ690WP or TCR790WP, configuration should be specified as:

```
miele:
  sensors:
   - id: sensor.tumble_dryer_program
     program_ids:
      - value_raw: 1
        value: automatic_plus
      - value_raw: 2
        value: cottons
      - value_raw: 3
        value: minimum_iron
      - value_raw: 4
        value: woollens_handcare
      - value_raw: 5
        value: delicates
      - value_raw: 6
        value: warm_air
      - value_raw: 7
        value: cool_air
      - value_raw: 8
        value: express
      - value_raw: 9
        value: cottons_eco
      - value_raw: 10
        value: gentle_smoothing
      - value_raw: 12
        value: proofing
      - value_raw: 13
        value: denim
      - value_raw: 14
        value: shirts
      - value_raw: 15
        value: sportswear
      - value_raw: 16
        value: outerwear
      - value_raw: 17
        value: silks_handcare
      - value_raw: 19
        value: standard_pillows
      - value_raw: 22
        value: basket_program
      - value_raw: 24
        value: steam_smoothing
      - value_raw: 31
        value: bed_linen
```

### Supported program names

It is not possible to customize program names. For adding new programs or translations, a PR is more than welcome. Below a list of supported program names.

Washing machine / Washer dryer:
- `cottons`
- `cottons_eco`
- `cottons_hygiene`
- `eco_40_60`
- `minimum_iron`
- `delicates`
- `woollens`
- `silks`
- `automatic_plus`
- `quick_power_wash`
- `express_20`
- `shirts`
- `dark_garments`
- `denim`
- `sportswear`
- `outerwear`
- `first_wash`
- `trainers`
- `pillows`
- `down_filled_items`
- `down_duvets`
- `curtains`
- `proofing`
- `starch`
- `rinse`
- `separate_rinse_starch`
- `drain_spin`
- `cool_air`
- `warm_air`
- `steam_care`
- `freshen_up`
- `clean_machine`
- `rinse_out_lint`

Tumble dryer:
- `cottons`
- `cottons_eco`
- `cottons_hygiene`
- `minimum_iron`
- `gentle_minimum_iron`
- `automatic_plus`
- `woollens_handcare`
- `delicates`
- `warm_air`
- `cool_air`
- `express`
- `gentle_smoothing`
- `proofing`
- `denim`
- `gentle_denim`
- `sportswear`
- `outerwear`
- `silks_handcare`
- `standard_pillows`
- `basket_program`
- `smoothing`
- `steam_smoothing`
- `bed_linen`
- `shirts`

Dishwasher:
- `intensive`
- `maintenance`
- `eco`
- `automatic`
- `normal`
- `solar_save`
- `gentle`
- `extra_quiet`
- `hygiene`
- `quick_power_wash`
- `tall_items`
- `glasses_warm`

Oven:
- `defrost`
- `eco_fan_heat`
- `auto_roast`
- `full_grill`
- `economy_grill`
- `fan_plus`
- `intensive_bake`
- `conventional_heat`
- `top_heat`
- `fan_grill`
- `bottom_heat`
- `moisture_plus_fan_plus`
- `1_tray`
- `2_trays`
- `baking_tray`
- `steam_bake`

Robot vacuum cleaner:
- `auto`
- `spot`
- `turbo`
- `silent`

Coffee machine:
- `ristretto`
- `espresso`
- `coffee`
- `long_coffee`
- `cappuccino`
- `cappuccino_italiano`
- `latte_macchiato`
- `espresso_macchiato`
- `cafe_au_lait`
- `caffellatte`
- `flat_white`
- `very_hot_water`
- `hot_water`
- `hot_milk`
- `milk_foam`
- `black_tea`
- `herbal_tea`
- `fruit_tea`
- `green_tea`
- `white_tea`
- `japanese_tea`
- `appliance_rinse`
- `descaling`
- `brewing_unit_degrease`
- `milk_pipework_rinse`
- `appliance_rinse`
- `milk_pipework_clean`
