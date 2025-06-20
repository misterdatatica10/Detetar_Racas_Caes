import streamlit as st
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet50, ResNet50_Weights
import json
import os
from datetime import datetime
from breed_descriptions import BREED_DESCRIPTIONS

# Dicionário de raças de cães do ImageNet
IMAGENET_CLASSES = {
    'n02085620': 'Chihuahua',
    'n02085782': 'Japanese Spaniel',
    'n02085936': 'Maltese',
    'n02086079': 'Pekinese',
    'n02086240': 'Shih Tzu',
    'n02086646': 'Blenheim Spaniel',
    'n02086910': 'Papillon',
    'n02087046': 'Toy Terrier',
    'n02087394': 'Rhodesian Ridgeback',
    'n02088094': 'Afghan Hound',
    'n02088238': 'Basset Hound',
    'n02088364': 'Beagle',
    'n02088466': 'Bloodhound',
    'n02088632': 'Bluetick',
    'n02089078': 'Black and Tan Coonhound',
    'n02089867': 'Walker Hound',
    'n02089973': 'English Foxhound',
    'n02090379': 'Redbone',
    'n02090622': 'Borzoi',
    'n02090721': 'Irish Wolfhound',
    'n02091032': 'Italian Greyhound',
    'n02091134': 'Whippet',
    'n02091244': 'Ibizan Hound',
    'n02091467': 'Norwegian Elkhound',
    'n02091635': 'Otterhound',
    'n02091831': 'Saluki',
    'n02092002': 'Scottish Deerhound',
    'n02092339': 'Weimaraner',
    'n02093256': 'Staffordshire Bull Terrier',
    'n02093428': 'American Staffordshire Terrier',
    'n02093647': 'Bedlington Terrier',
    'n02093754': 'Border Terrier',
    'n02093859': 'Kerry Blue Terrier',
    'n02093991': 'Irish Terrier',
    'n02094114': 'Norfolk Terrier',
    'n02094258': 'Norwich Terrier',
    'n02094433': 'Yorkshire Terrier',
    'n02095314': 'Wire-haired Fox Terrier',
    'n02095570': 'Lakeland Terrier',
    'n02095889': 'Sealyham Terrier',
    'n02096051': 'Airedale',
    'n02096177': 'Cairn',
    'n02096294': 'Australian Terrier',
    'n02096437': 'Dandie Dinmont',
    'n02096585': 'Boston Bull',
    'n02097047': 'Miniature Schnauzer',
    'n02097130': 'Giant Schnauzer',
    'n02097209': 'Standard Schnauzer',
    'n02097298': 'Scotch Terrier',
    'n02097474': 'Tibetan Terrier',
    'n02097658': 'Silky Terrier',
    'n02098105': 'Soft-coated Wheaten Terrier',
    'n02098286': 'West Highland White Terrier',
    'n02098413': 'Lhasa',
    'n02099267': 'Flat-coated Retriever',
    'n02099429': 'Curly-coated Retriever',
    'n02099601': 'Golden Retriever',
    'n02099712': 'Labrador Retriever',
    'n02099849': 'Chesapeake Bay Retriever',
    'n02100236': 'German Short-haired Pointer',
    'n02100583': 'Vizsla',
    'n02100735': 'English Setter',
    'n02100877': 'Clumber',
    'n02101006': 'English Springer',
    'n02101388': 'Brittany',
    'n02101556': 'Clumber Spaniel',
    'n02102040': 'English Springer Spaniel',
    'n02102177': 'Welsh Springer Spaniel',
    'n02102318': 'Cocker Spaniel',
    'n02102480': 'Sussex Spaniel',
    'n02102973': 'Irish Water Spaniel',
    'n02104029': 'Kuvasz',
    'n02104365': 'Schipperke',
    'n02105056': 'Groenendael',
    'n02105162': 'Malinois',
    'n02105251': 'Briard',
    'n02105412': 'Kelpie',
    'n02105505': 'Komondor',
    'n02105641': 'Old English Sheepdog',
    'n02105855': 'Shetland Sheepdog',
    'n02106030': 'Collie',
    'n02106166': 'Border Collie',
    'n02106382': 'Bouvier des Flandres',
    'n02106550': 'Rottweiler',
    'n02106662': 'German Shepherd',
    'n02107142': 'Doberman',
    'n02107312': 'Miniature Pinscher',
    'n02107574': 'Greater Swiss Mountain Dog',
    'n02107683': 'Bernese Mountain Dog',
    'n02107908': 'Appenzeller',
    'n02108000': 'EntleBucher',
    'n02108089': 'Boxer',
    'n02108422': 'Bull Mastiff',
    'n02108551': 'Tibetan Mastiff',
    'n02108915': 'French Bulldog',
    'n02109047': 'Great Dane',
    'n02109525': 'Saint Bernard',
    'n02109961': 'Eskimo Dog',
    'n02110063': 'Malamute',
    'n02110185': 'Siberian Husky',
    'n02110341': 'Dalmatian',
    'n02110627': 'Affenpinscher',
    'n02110806': 'Basenji',
    'n02110958': 'Pug',
    'n02111129': 'Leonberg',
    'n02111277': 'Newfoundland',
    'n02111500': 'Great Pyrenees',
    'n02111889': 'Samoyed',
    'n02112018': 'Pomeranian',
    'n02112137': 'Chow',
    'n02112350': 'Keeshond',
    'n02112706': 'Brabancon Griffon',
    'n02113023': 'Pembroke',
    'n02113186': 'Cardigan',
    'n02113624': 'Toy Poodle',
    'n02113712': 'Miniature Poodle',
    'n02113799': 'Standard Poodle',
    'n02113978': 'Mexican Hairless'
}

# Configurar a página do Streamlit
st.set_page_config(
    page_title="Identificador de Raças de Cães",
    page_icon="🐕",
    layout="wide"
)

# Inicializar o histórico no session state se não existir
if 'historico' not in st.session_state:
    st.session_state.historico = []

# Barra lateral para configurações
with st.sidebar:
    st.title("⚙️ Configurações")
    confidence_threshold = st.slider(
        "Nível de Confiança",
        min_value=1.0,
        max_value=100.0,
        value=5.0,
        help="Ajuste o nível mínimo de confiança para exibir previsões"
    )
    
    st.title("📜 Histórico")
    if st.session_state.historico:
        for item in st.session_state.historico[-5:]:  # Mostrar últimas 5 análises
            with st.expander(f"{item['data']} - {item['raca']}"):
                st.write(f"Confiança: {item['confianca']:.2f}%")

# Título e descrição
st.title("🐕 Identificador de Raças de Cães")
st.write("Carregue uma fotografia de um cão para identificar a sua raça!")

# Opções de entrada de imagem
input_method = st.radio(
    "Escolha como pretende fornecer a imagem:",
    ["Carregar Ficheiro", "Câmara"],
    horizontal=True
)

# Variável para armazenar a imagem
img = None

if input_method == "Carregar Ficheiro":
    uploaded_file = st.file_uploader("Escolha uma imagem...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert('RGB')
else:
    camera_image = st.camera_input("Tire uma fotografia do cão")
    if camera_image is not None:
        img = Image.open(camera_image).convert('RGB')

@st.cache_resource
def load_model():
    # Carregar o modelo pré-treinado
    model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
    model.eval()
    return model

def process_image(image):
    # Melhorar o pré-processamento da imagem
    transform = transforms.Compose([
        transforms.Resize((256, 256)),  # Redimensionar mantendo proporções
        transforms.CenterCrop(224),     # Cortar o centro
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    # Aplicar transformações
    return transform(image).unsqueeze(0)

def is_dog_class(class_name):
    # Lista expandida de palavras-chave relacionadas a cães
    dog_keywords = [
        'dog', 'hound', 'terrier', 'shepherd', 'pug', 'beagle', 'collie',
        'retriever', 'spaniel', 'husky', 'poodle', 'bulldog', 'rottweiler',
        'mastiff', 'labrador', 'boxer', 'doberman', 'chihuahua', 'pomeranian',
        'chow', 'corgi', 'dachshund'
    ]
    class_name = class_name.lower()
    return any(keyword in class_name for keyword in dog_keywords)

if img is not None:
    try:
        # Criar duas colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(img, caption='Imagem carregada', use_column_width=True)
        
        with col2:
            with st.spinner('A analisar a imagem...'):
                # Processar a imagem
                input_tensor = process_image(img)
                
                # Fazer previsão
                model = load_model()
                with torch.no_grad():
                    output = model(input_tensor)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)
                
                # Obter as 10 principais previsões
                top10_prob, top10_idx = torch.topk(probabilities, 10)
                
                # Converter índices para nomes de classes
                class_names = ResNet50_Weights.IMAGENET1K_V2.meta["categories"]
                
                # Filtrar e mostrar previsões de cães
                dog_predictions = []
                for prob, idx in zip(top10_prob, top10_idx):
                    class_name = class_names[idx]
                    confidence = prob.item() * 100
                    if is_dog_class(class_name) and confidence > confidence_threshold:
                        dog_predictions.append((class_name, confidence))
                
                if dog_predictions:
                    st.success("Raças de cão identificadas:")
                    for breed, confidence in dog_predictions:
                        st.write(f"### {breed}")
                        st.write(f"Confiança: {confidence:.2f}%")
                        
                        # Adicionar ao histórico
                        st.session_state.historico.append({
                            'data': datetime.now().strftime("%Y-%m-%d %H:%M"),
                            'raca': breed,
                            'confianca': confidence
                        })
                        
                        # Tentar encontrar correspondência aproximada
                        breed_lower = breed.lower()
                        found_match = False
                        for known_breed in BREED_DESCRIPTIONS:
                            if known_breed.lower() in breed_lower or breed_lower in known_breed.lower():
                                info = BREED_DESCRIPTIONS[known_breed]
                                st.write("#### Informações da Raça")
                                st.write(f"**Temperamento:** {info['temperamento']}")
                                st.write(f"**Tamanho:** {info['tamanho']}")
                                st.write(f"**Peso:** {info['peso']}")
                                st.write(f"**Expectativa de Vida:** {info['expectativa_vida']}")
                                st.write(f"**Descrição:** {info['descricao']}")
                                found_match = True
                                break
                        
                        if not found_match:
                            st.warning("Informações detalhadas não disponíveis para esta raça específica.")
                else:
                    st.warning("Não foi possível identificar um cão na imagem com confiança suficiente.")
                    st.info("Dicas para melhor reconhecimento:\n" +
                           "1. Utilize uma imagem bem iluminada\n" +
                           "2. Certifique-se de que o cão está de frente para a câmara\n" +
                           "3. Evite imagens muito escuras ou desfocadas\n" +
                           "4. O focinho do cão deve estar visível na fotografia")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar a imagem: {str(e)}")
        st.info("Por favor, tente novamente com outra imagem.")

# Adicionar seção de informações no final
st.markdown("---")
st.markdown("""
### 📝 Sobre o Projeto
Este identificador de raças de cães utiliza um modelo de inteligência artificial pré-treinado para reconhecer diferentes raças de cães.
Para melhores resultados:
- Use fotografias bem iluminadas
- Certifique-se que o cão está claramente visível
- Evite fotografias com vários cães
- Dê preferência a fotografias onde o cão está a olhar para a câmara
""")

# Configuração da porta para o Render
port = int(os.environ.get("PORT", 8501)) 