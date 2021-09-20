def loss_overblow_freqs(peak, target):
    loss=0
    for i in range(len(target)):
        loss += abs(target[i] - peak.impedance_peaks[i]["freq"])
    return loss   


def mutate(geo, operation):    

    if operation=="change_length":
        factor=0.95+(random.random()/10)
        geo.stretch(factor)
        
    elif operation=="change_segment_diameter":
        factor=0.75+(random.random()/50)
        segment=random.randint(0, len(geo.geo)-1)
        
        if segment==0:
            return mutate(geo, operation)
        geo.geo[segment][1]*=factor
        
    elif operation=="change_segment_position":
        factor=0.75+(random.random()/50)
        segment=random.randint(0, len(geo.geo)-1)
        geo.geo[segment][0]*=factor
        
    else:
        raise Exception("unknown operation " + str(operatino))
        
    return geo

def evolve(geo, target):
    
    generation_size=10
    n_generations=100
    mutation_operations=["change_length", "change_segment_diameter", "change_segment_position"]
    
    peak, fft=didgmo_bridge(geo)
    father_loss=loss_overblow_freqs(peak, target)
    
    best_loss=father_loss
    best_geo=geo
    
    DidgeVisualizer.vis_didge(geo)
    FFTVisualiser.vis_fft_and_target(fft, target)
    return
    
    with tqdm(total=n_generations*generation_size, bar_format='{l_bar}{bar:30}{r_bar}{bar:-10b}') as pbar:

        for i_gen in range(n_generations):

            loss_before_mutate=best_loss
            for i_mutant in range(generation_size):
                mutation_operation=mutation_operations[random.randint(0, len(mutation_operations)-1)]
                mutant=geo.copy()
                mutant=mutate(mutant, mutation_operation)
                peak=didgmo_bridge(mutant, skip_fft=True)
                
                #peak.print_impedance_peaks()

                
                mutant_loss=loss_overblow_freqs(peak, target)
                if mutant_loss<best_loss:
                    best_geo=mutant
                    best_loss=mutant_loss

                p=i_gen*generation_size + i_mutant
                pbar.update(1)
                pbar.set_description(f"generation={i_gen}, loss={best_loss:.2f}, loss_diff={loss_before_mutate-best_loss}")
            loss_diff=loss_before_mutate-best_loss        
    return best_geo
            