level_max_x = 9999
data.prev_lives = 3
data.initial_energy = 52

data.offset_x = nil
end_x = nil
data.prev_progress = 0
data.xpos_last_x = nil

energy_multiplier = 5
score_multiplier = 10
data.last_score = 0
data.last_energy = nil

function clip(original_value, min, max)
    if original_value < min then
        return min
    elseif original_value > max then
        return max
    else
        return original_value
    end
end

function calc_progress(data)
    if data.offset_x == nil then
        data.offset_x = -data.relative_x_pos
        end_x = level_max_x - data.relative_x_pos
    end
    local cur_x = clip(data.relative_x_pos + data.offset_x, 0, end_x)
    return cur_x / end_x
end

function xpos_done()
    -- Only play one live
    if data.lives < data.prev_lives then
        return true
    end
    return data.relative_x_pos > level_max_x
end

function xpos_reward()
    if data.xpos_last_x == nil then
        data.xpos_last_x = data.relative_x_pos
    end
    if data.last_energy == nil then
        data.last_energy = data.initial_energy
    end

    -- X coordinate can increment or decrement, score increments, energy decrements
    local result = data.relative_x_pos - data.xpos_last_x + (data.score - data.last_score)*score_multiplier - (data.last_energy - data.energy)*energy_multiplier

    data.last_score = data.score
    data.last_energy = data.energy
    data.xpos_last_x = data.relative_x_pos
    return result
end
