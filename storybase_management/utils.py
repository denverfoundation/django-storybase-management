def find_closest(items, target_val):
    closest = None
    min_diff = None
    
    for item in items:
        if item['value'] == target_val:
            closest = item
            break
        
        diff = abs(item['value'] - target_val)
        if closest is None or diff < min_diff:
            closest = item
            
    return closest

def model_stats(qs, val_getter, id_attr, story_id_getter):
    vals = []
    total = 0
    min_val = {
        id_attr: None,
        'value': 0,
        'story_id': None,
    }
    max_val = {
        id_attr: None,
        'value': 0,
        'story_id': None,
    }

    for model in qs:
        val = val_getter(model)
        if val:
            val_dict = {
                id_attr: getattr(model, id_attr),
                'value': val,
                'story_id': story_id_getter(model),
            }
            vals.append(val_dict)
            total = total + val

            if min_val[id_attr] is None or val < min_val['value']:
                min_val = val_dict
            elif val > max_val['value']:
                max_val = val_dict

    avg = total / len(vals)
    closest = find_closest(vals, avg)
    
    return (min_val, max_val, closest)

