from django.shortcuts import render
# En la vista se debe considera el modelo que se va usar
from .models import Cliente

# consulta_clientes es la vista que muestra la lista
def consulta_clientes(request):
    # Se requiere obtner los datos a gestionar
    #clientes = Cliente.objects.all().order_by('ape_nom') # la data es la que se requiera 
    clientes = Cliente.objects.all().order_by('id_cliente') # la data es la que se requiera 
    # Estos datos deben estar disponibles para una plantilla (Template)
    # Se crea un diccionario llamado context (será accesible desde la plantilla)
    context = { # en el template será objetos y valores
        'clientes' : clientes,
        'titulo'   : 'Lista de Clientes',
        'mensaje'  : 'Hola'
    }
    # Se devolverá el enlace entre la plantilla y el contexto
    return render(request, r'venta\lista_clientes.html', context)

from .forms import ClienteCreateForm, ClienteUpdateForm
from django.contrib import messages
from django.shortcuts import redirect

def crear_cliente(request):
    dni_duplicado = False

    if request.method == 'POST':
        form = ClienteCreateForm(request.POST)
        if form.is_valid():
            form.save() # salvar los datos
            messages.success(request, 'Cliente registrado correctamente')
            print('Se guardó bien')
            return redirect('crear_cliente') # se redirecciona a la misma página
        else:
            if 'id_cliente' in form.errors:
                for error in form.errors['id_cliente']:
                    if str(error) == "DNI_DUPLICADO": # se recibe del raise de forms
                        dni_duplicado = True
                        # Limpiar los errores 
                        form.errors['id_cliente'].clear()
                        print('DNI Duplicado!')
                        break

    else:
        form = ClienteCreateForm() # No hace nada, devuelve la misma pantalla

    context = {
        'form':form,
        'dni_duplicado':dni_duplicado # Enviar el estado del dni duplicado
    }
    return render(request, 'venta/crear_cliente.html', context)    

def actualizar_cliente(request):
    cliente = None
    dni_buscado = None
    form = None

    if request.method == 'POST':
        if 'buscar' in request.POST:
            # Buscar el cliente por DNI
            dni_buscado = request.POST.get('dni_busqueda')
            if dni_buscado:
                try: # intentar considerar la busqueda del cliente
                    # Obtener un objeto del tipo cliente
                    cliente = Cliente.objects.get(id_cliente=dni_buscado)
                    # Crear un formulario con los datos del objeto cliente
                    form = ClienteUpdateForm(instance=cliente)
                    messages.success(request, f'Cliente con DNI {dni_buscado} encontrado')
                except Cliente.DoesNotExist: # execepcion de dato no existente
                    messages.error(request, 'No se encontró Cliente con ese DNI')    
            else:
                messages.error(request, 'Por favor ingrese el DNI para buscar') 
        elif 'guardar' in request.POST:
            dni_buscado = request.POST.get('dni_busqueda') or request.POST.get('id_cliente')
            if dni_buscado:
                try:
                    cliente = Cliente.objects.get(id_cliente = dni_buscado)
                    form = ClienteUpdateForm(request.POST, instance=cliente)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Cliente actualizado correctamente')
                        # formulario con datos actualizados
                        cliente.refresh_from_db()
                        # devolver al formulario
                        form = ClienteUpdateForm(instance=cliente)
                    else:
                        messages.error(request, 'Error en los datos del formulario')
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
                    

            else:
                messages.error(request, 'No se puede identificar al cliente para actaualizar')
    context = {
        'form':form,
        'dni_buscado': dni_buscado,
        'cliente_encontrado': cliente is not None,
        'cliente':cliente
    }
    return render(request,'venta/u_cliente.html', context)
                     
# Eliminar clientes
def borrar_cliente(request):
    clientes_encontrados = []
    tipo_busqueda = 'dni'  # Por defecto búsqueda por DNI
    termino_busqueda = ''
    total_registros = 0
    
    if request.method == 'POST':
        if 'consultar' in request.POST:
            # Realizar búsqueda
            tipo_busqueda = request.POST.get('tipo_busqueda', 'dni')
            termino_busqueda = request.POST.get('termino_busqueda', '').strip()
            
            if termino_busqueda:
                if tipo_busqueda == 'dni':
                    # Búsqueda exacta por DNI
                    try:
                        cliente = Cliente.objects.get(id_cliente=termino_busqueda)
                        clientes_encontrados = [cliente]
                    except Cliente.DoesNotExist:
                        messages.error(request, 'No se encontró cliente con ese DNI')
                        
                elif tipo_busqueda == 'nombre':
                    # Búsqueda por coincidencia en apellidos y nombres
                    clientes_encontrados = Cliente.objects.filter(
                        ape_nom__icontains=termino_busqueda
                    ).order_by('id_cliente')
                    
                    if not clientes_encontrados:
                        messages.error(request, 'No se encontraron clientes con ese nombre')
                
                total_registros = len(clientes_encontrados)
                
                if total_registros > 0:
                    messages.success(request, f'Se encontraron {total_registros} registro(s)')
            else:
                messages.error(request, 'Por favor ingrese un término de búsqueda')
                
        elif 'eliminar' in request.POST:
            # Eliminar cliente específico
            dni_eliminar = request.POST.get('dni_eliminar')
            
            if dni_eliminar:
                try:
                    cliente = Cliente.objects.get(id_cliente=dni_eliminar)
                    cliente.delete()
                    messages.success(request, f'Cliente con DNI {dni_eliminar} eliminado correctamente')
                    
                    # Volver a hacer la búsqueda para actualizar la lista
                    tipo_busqueda = request.POST.get('tipo_busqueda_actual', 'dni')
                    termino_busqueda = request.POST.get('termino_busqueda_actual', '')
                    
                    if termino_busqueda:
                        if tipo_busqueda == 'dni':
                            # Para DNI, no mostrar nada ya que se eliminó
                            clientes_encontrados = []
                        elif tipo_busqueda == 'nombre':
                            # Actualizar lista por nombre
                            clientes_encontrados = Cliente.objects.filter(
                                ape_nom__icontains=termino_busqueda
                            ).order_by('id_cliente')
                        
                        total_registros = len(clientes_encontrados)
                        
                except Cliente.DoesNotExist:
                    messages.error(request, 'Cliente no encontrado')
    
    context = {
        'clientes_encontrados': clientes_encontrados,
        'tipo_busqueda': tipo_busqueda,
        'termino_busqueda': termino_busqueda,
        'total_registros': total_registros
    }
    
    return render(request, 'venta/borrar_cliente.html', context)