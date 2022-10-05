import numpy as np
import json

def transformJsonString(jsonString):
    return json.loads(jsonString)

def prepare(jsonString):

    json = transformJsonString(jsonString)
    positions, values, gyro_raw = transform_to_python_input(json)
    positions, values = clean_all_zeros(positions, values) #probar __KP?
    clustered_patches, joined_patches, joined_Gyro = find_and_join_clusters__KP(positions, values, gyro_raw)
    Gyro = [g[0] for g in joined_Gyro] # MEJORAR ESTO CLARAMENTE!!!

    processed_patches, index_max_list = zip(*[shorten_long_patch_using_max_240__KP(jp) for jp in joined_patches] )

    IP_dobleces, dDoble, profValle, pico_leader = zip(*[number_of_uds_KP(jp, 17) for jp in joined_patches] ) #PUEDO SUBIRLO

    ip_posiciones = list(np.array(index_max_list) + np.array([positions[i[0]] for i in clustered_patches]))
    multiScore = [p - 30 + d * 30/200 for p, d in zip(profValle, dDoble)]  # --> Si multiScore es negativo, no puede ser pico múltiple

    fourier_transform_array = []
    scores_is_pic_array = []
    scores_is_sign_array = []

    for patch in processed_patches:
        tr = transformadaFourierEficiente_np(patch)
        fourier_transform_array.append(tr)


    # return processed_patches, ip_posiciones, multiScore, Gyro, fourier_transform_array
    return fourier_transform_array




def transform_to_python_input(json):
    positions = np.array(string_array_to_array(json["positions"]))
    positions = clean_extra_zeros(positions)
    
    values = json["values"]
    print('valores:')
    print(values)
    print('jotason:')
    print(json)
    values = np.array(values)
    values = np.abs(values)

    gyro = np.array(string_array_to_array(json["gyro"]))
    
    if (not "localpositions" in json):
        return positions, values, gyro
    else:
        unrolled_local_positions = string_array_to_array(json["localpositions"])
        unrolled_local_positions = clean_extra_zeros(unrolled_local_positions)

        clean_values = []
        for i in range(len(unrolled_local_positions)):
            local_position = unrolled_local_positions[i]
            value = values[i]
 
            if local_position > 80:
                rolled_value = np.roll(value, 79 - local_position)
            else:
                rolled_value = value
            
            clean_values.append(rolled_value)
        return positions, clean_values, gyro


def string_array_to_array(strn):
    strn_clean =  strn.replace("[", "").replace("]", "")
    arr = strn_clean.split(",")
    return [int(item) for item in arr]

def clean_extra_zeros(arr):
    result = []
    for el in arr:
        if el != 0:
            result.append(el)
    return result
    

def clean_all_zeros(positions, values):
    vals_copy = list(values)
    pos_copy = list(positions)
    for i in range(len(vals_copy)):
        if 0 in vals_copy[i]:
            positPrimer0 = list(vals_copy[i]).index(0)
            promediator = int(np.mean(vals_copy[i][:positPrimer0]))
            # Luego se corta hacia la derecha...
            producto = np.ones(len(vals_copy[i]) - positPrimer0) * promediator
            vals_copy[i] = list(vals_copy[i][:positPrimer0]) + list(producto)
            print(vals_copy[i])
    if 0 in pos_copy:
        pos_copy = pos_copy[:pos_copy.index(0)]
    return pos_copy, vals_copy
    
def join_pieces(v, w, repeated_length):
    result = []
    for i in range(0, len(v)-repeated_length):
        result.append(v[i])
    for j in range(0, len(w)):
        result.append(w[j])
    return result


# SOLO HE LIMPIANDO UN POQUTIO, PERO LO DE ARRIBA ES TODAVÍA IDÉNTICO A LO QUE YA TENÍAMOS!!
# AÑADO LOS GIROS ARREJUNTADOS PARA PROBAR DIFERENTES COSITAS
def find_and_join_clusters__KP(positions, values, giros):
    clustered_patches_indexes = [[0]]
    joined_patches = [values[0]]
    joined_Gyro = [[giros[0]]]
    for i in range(1, len(positions)): #Por defeccto, va de 1 en 1!!!
        diff = positions[i] - positions[i - 1]
        if diff < len(values[i-1]):  # O igual?? (Puede ser diff = 0?)
            clustered_patches_indexes[len(clustered_patches_indexes) - 1].append(i)
            current_piece = joined_patches[len(clustered_patches_indexes) - 1] #El anterior joined_patches??
            joined_patches[len(clustered_patches_indexes) - 1] = join_pieces(current_piece, values[i], len(values[i-1]) - diff)
            joined_Gyro[len(clustered_patches_indexes) - 1].append(giros[i])
        else:
            clustered_patches_indexes.append([i])
            joined_patches.append(values[i])
            joined_Gyro.append([giros[i]])
    return clustered_patches_indexes, joined_patches, joined_Gyro # Lo nuevo es que ahora incorporo el giro!!!

def shorten_long_patch_using_max_240__KP(long_patch):
# ''' Elijo el representante que tenga el valor más alto. (De "v", no de "DA"!) '''
    index_max = max_index(DA(long_patch, suavizado = True)) + 9 # DPM!!! YA LO ESTABA CALCULANDO!!
    indexMin = index_max-80
    indexMax = index_max + 160 #(este en cambio justaente no estará incluido: "v[incuido : NO incluido]" )
    media = np.mean(long_patch)
    result = list(media*np.ones(abs(indexMin) if indexMin<0 else 0)) + list(long_patch[max(indexMin, 0):min(len(long_patch), indexMax)]) + list( media * np.ones( (indexMax-len(long_patch)) if indexMax>len(long_patch) else 0 ) ) # si me paso cn :len(long_patch) no pasa nada
    result = list( np.array(result)-np.mean(result) ) # NUEVO, TESTAR!!!! EN CASO DE PIRAMIDUSOIDE NO HARÍA FALTA!?
    return result, index_max

def max_index(v):
    index_max = 0
    for i in range(0, len(v)):
        if v[i] > v[index_max]:
            index_max = i
    return index_max

def DA(v, suavizado=False, ENE=8):
    # La dimensión es la de v -1
    DifAcumulada = np.absolute(np.array(v[1:])-np.array(v[:-1]))
    if suavizado:
        DifAcumulada = valoresAgrupados(DifAcumulada, ENE)
    # DifAcumulada = diferencias
    return DifAcumulada

ENE = 8

def valoresAgrupados(v, N=ENE):
    # AGRUPA SUMANDO EL ÚLTIMO VALOR A LOS N ÚLTIMOS DEL VECTOR v
    w = np.array(list(v))
    w0 = np.array(list(w[N:]))
    for i in range(1, N+1, 1):
        w0 += w[N-i:-i]
    return list(w[:N])+list(w0)

# Conteo de unidades para picos clasificados como 5s
def number_of_uds_KP(data, suavizado=20, Gyro=0):  # 17
    '''Devuelve el número de unidades que un pico "5" suma'''
   
    clean = np.absolute(np.array(data[1:])-np.array(data[:-1]))
    smooth = smooth_gaussian(clean, suavizado)
    maxs, mins = calculate_extrema__KP(smooth)
    
    if(maxs[0][0] == 0): maxs.pop(0)

    if len(maxs)>1:
      # if verbose: print("Entro en el selecto club")
      mv = maximos_validos_v6(maxs, mins)#, draw)
      return len(mv[0]), mv[1], mv[2], mv[3]
    else:
      return 1, 0, 0, 0

def smooth_gaussian(v, sigma):
    sd = float(sigma)
    # make the radius of the filter equal to truncate standard deviations
    radius = int(4.0 * sd + 0.5)
    sigma2 = sigma * sigma
    phi_x = []
    sum = 0
    for x in range(-radius, radius+1):
        phi_x_item = np.exp(-0.5 / sigma2 * x ** 2)
        phi_x.append(phi_x_item)
        sum = sum + phi_x_item
    phi_x = np.asarray(phi_x)
    phi_x = phi_x / sum
    weights = phi_x[::-1]
    result = convolution_correlate_1d(v, weights)
    return np.asarray(result)

def convolution_correlate_1d(v, w):
    result = []
    r = len(w)//2
    for i in range(0, len(v)):
        divisor = 0
        val = 0
        for k in range(-r, r+1):
            if 0 <= i + k < len(v):
                val = val + v[i + k] * w[k + r]
                divisor += w[k + r]
        result.append(val/divisor)
    return result


def calculate_extrema__KP(v, umbral=0.4):
    v = list(v)
    # Se calcula el umbral sobre máximos locales
    span = 152  # Tiene que ser PAR
    max_span = []
    for i in range(len(v)-span):
        max_span.append(max(v[i:i+span]))
    max_span = [max_span[0]]*(span//2) + max_span + [max_span[-1]]*(span//2)

    umbral_local = [max(3, umbral*m) for m in max_span]  # reducción del máximo + mínimo absoluto
    maxs = []
    mins = []

    if v[0] > v[1]:
        maxs.append([0, v[0]])
    if v[0] <= v[1]:
        mins.append([0, v[0]])
    for i in range(1, len(v) - 1):
        if v[i-1] < v[i] > v[i + 1] and v[i] > umbral_local[i]:
            maxs.append([i, v[i]])
        elif (v[i - 1] == v[i] > v[i + 1]):
            if i > 1 and v[i] > umbral_local[i]:
                if maxs==[]: maxs.append([i, v[i]])  # El ÚNICO extremo fue un mínimo
                elif maxs[-1][0] < mins[-1][0]: maxs.append([i, v[i]])  # El ÚLTIMO extremo fue un mínimo
        elif (v[i - 1] > v[i] < v[i + 1]):
            mins.append([i, v[i]])
        elif (v[i - 1] == v[i] < v[i + 1]):
            if i > 1:
                if mins==[]:
                    mins.append([i, v[i]])  # El ÚNICO extremo fue un máximo
                elif maxs==[]: pass
                elif maxs[-1][0] > mins[-1][0]: mins.append([i, v[i]])  # El ÚLTIMO extremo fue un máximo
    if v[-1] <= v[-2]:
        mins.append([len(v)-1,v[-1]])
    elif v[-1] > v[-2]:
        maxs.append([len(v)-1,v[-1]])
    if len(maxs):
        # print(maxs, mins)
        return maxs, mins
    else:
        return [[v.index(max(v)), max(v)]], []


def maximos_validos_v6(maxs, mins):#, draw):
    maxValidos = [maxs[0]]
    minValidos = []
    if len(maxs) ==1: return maxValidos, 0, 0, 0
    for i in range(1, len(maxs), 1):
        value = valorIntermedioMin(maxs[i-1][0], maxs[i][0], mins)
        if value: # Cuidado! Si el resultado es cero, hay que tener cuidado! Mejor devolver el valor!
            if value[1] < maxs[i-1][1]*0.95 and value[1] < maxs[i][1]*0.95:
                maxValidos.append(maxs[i])
                minValidos.append(value)
            elif maxs[i][1] > maxValidos[-1][1]:
                maxValidos[-1] = maxs[i]
    x1 = [i[0] for i in maxValidos]
    y1 = [i[1] for i in maxValidos]
    x2 = [i[0] for i in minValidos]
    y2 = [i[1] for i in minValidos]
    IndexMaxPrincipal = y1.index(max(y1))
    if len(y1[:IndexMaxPrincipal]+y1[IndexMaxPrincipal+1:]) > 0:
        IndexMaxSecundario = y1.index(max(y1[:IndexMaxPrincipal]+y1[IndexMaxPrincipal+1:]))
        IndexMin = y2.index( min( y2[min(IndexMaxPrincipal, IndexMaxSecundario) : max(IndexMaxPrincipal, IndexMaxSecundario)] ) )
        distPicos = abs(x1[IndexMaxPrincipal]-x1[IndexMaxSecundario])
        profundidadValle = y1[IndexMaxSecundario] - y2[IndexMin]
        picoLeader = 0 if IndexMaxPrincipal < IndexMaxSecundario else 1
    else:
        distPicos = 0
        profundidadValle = 0
        picoLeader = 0
    return maxValidos, distPicos, profundidadValle, picoLeader

def valorIntermedioMin(a, b, mins):
    for i in range(len(mins)):
        if a < mins[i][0] < b:
            return mins[i]
    return False


NFFTmaxEfic = 20
sinMatrix = np.sin([[j*i*np.pi/NFFTmaxEfic for j in range(NFFTmaxEfic)] for i in range(NFFTmaxEfic)])
cosMatrix = np.cos([[j*i*np.pi/NFFTmaxEfic for j in range(NFFTmaxEfic)] for i in range(NFFTmaxEfic)])

def transformadaFourierEficiente_np(res, N=NFFTmaxEfic):
    resMatrix = np.stack([res[i:len(res)-N+1+i] for i in range(N)], axis=1).astype(float)
    resMatrix -= np.mean(resMatrix, axis=0)
    return np.sqrt((resMatrix @ sinMatrix)**2 + (resMatrix @ cosMatrix)**2) /400.
