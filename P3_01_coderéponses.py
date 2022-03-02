#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# In[2]:


population = pd.read_csv("fr_population.csv")
cereal = pd.read_csv("fr_cereales.csv")
sous_alimentation = pd.read_csv('fr_sousalimentation.csv')
vegetal = pd.read_csv('fr_vegetaux.csv')
animal = pd.read_csv('fr_animaux.csv')


# # Question 1 : Calculez le nombre d'humains sur terre 

# In[3]:


world_population = 1000 * population["Valeur"].sum()
world_population


# La population mondiale de 2013 est largement supérieure à celle de nos jours ce qui est une erreur. On constate que la population de la chine est comptée en double. Suppression de la valeur de la population globale de la chine pour garder celle des sous-régions. 

# In[4]:


indexChine = population[ population['Symbole'] == 'A' ].index
population.drop(indexChine, inplace=True)
nb_people = 1000 * population["Valeur"].sum()
nb_people


# Le résultat obtenu semble plus cohérent avec la population mondiale en 2013

# # Question 2:

# In[5]:


# Création d'un dataframe végétaux en fonction des pays et des produits
vegetal_produit = vegetal.pivot_table(index=['Zone','Produit'], columns='Élément', values=['Valeur'])
vegetal_produit.fillna(0, inplace=True)

#Disponibilité intérieure du blé en France
ble = vegetal_produit.loc['France','Blé']
dispo_int_ble_fr = ble['Valeur']['Disponibilité intérieure']
dispo_int_ble_fr


# In[6]:


dispo_int_ble_fr_2 = ble['Valeur']['Production'] + ble['Valeur']['Importations - Quantité'] - ble['Valeur']['Exportations - Quantité'] + ble['Valeur']['Variation de stock']
dispo_int_ble_fr_2


# In[7]:


population_pivot = population.pivot_table(index='Zone', columns='Élément', values='Valeur')
population_pivot['Population totale'] = population_pivot['Population totale'] * 1000
population_fr = population_pivot.loc[('France'),'Population totale']

dispo_int_ble_fr_3 = ble['Valeur']['Semences'] + ble['Valeur']['Pertes'] + ble['Valeur']['Aliments pour animaux'] + (((ble['Valeur']['Disponibilité alimentaire en quantité (kg/personne/an)']*population_fr)/1000)/1000) + ble['Valeur']['Traitement'] +ble['Valeur']['Autres utilisations (non alimentaire)']
dispo_int_ble_fr_3


# On constate qu'à un chiffre après la virgule dispo_int_ble_fr = dispo_int_ble_fr_1 = dispo_int_ble_fr_2

# # Création d'un Dataframe général

# In[8]:


# création d'une colonne type dans les dataframes 
vegetal['Type'] = 'vegetal'
animal['Type'] = 'animal'
cereal['is_cereal'] = True

vegetal = vegetal[vegetal['Zone'] != 'Chine' ].copy()
animal = animal[animal['Zone'] != 'Chine'].copy()
population = population[population['Zone'] != 'Chine'].copy()

#Union des deux Dataframes animal et vegetal
main_df = pd.concat([animal, vegetal])
# Création d'un tableau croisé dynamique
main_df = main_df.pivot_table(index=['Zone','Produit','Code Produit', 'Type','Code zone', 'Année'], columns='Élément', values=['Valeur'] )
main_df = main_df.reset_index()
anim_vegetal = main_df.copy()
# Ajout du dataframe Population
main_df = main_df.merge(population, on='Zone', how="left")
#Ajout du dataframe cereal
# remplacer les valeurs manquantes par 0
main_df.fillna(0, inplace=True)
main_df['Code produit'] = main_df['Code Produit','']


# Création d'une colonne 'Population_totale'
main_df['Population_totale'] = main_df['Valeur']*1000
main_df = main_df.drop(['Zone', 'Code zone','Code Domaine', 'Domaine' ,'Valeur' ,'Code Élément', ('Année', ''), 'Élément', 'Code Produit', 'Produit', 'Code année', 'Unité', 'Symbole', 'Description du Symbole'], axis=1)


main_df


# # Question 3:  Calculez (pour chaque pays et chaque produit) la disponibilité alimentaire en kcal puis en kg de protéines

# In[9]:


# Disponibilité alimentaire kcal par pays 
main_df['disp_alim_kcal_pays'] = main_df['Valeur', 'Disponibilité alimentaire (Kcal/personne/jour)'] * main_df['Population_totale'] * 365

# Disponibilité alimentaire kg par pays 
main_df['disp_alim_kg_an'] = (main_df['Valeur', 'Disponibilité de protéines en quantité (g/personne/jour)'] / 1000)*365
main_df['disp_alim_kg_pays'] = main_df['disp_alim_kg_an'] * main_df['Population_totale']
main_df


# ## Question 4 :

# In[10]:


# Calcul du ratio kcal/kg
main_df['ratio kcal/kg'] = (main_df['Valeur', 'Disponibilité alimentaire (Kcal/personne/jour)'] * main_df['Population_totale'] *365) /(main_df['Valeur', 'Nourriture']*1000000)

#poids total 
total_weight = main_df['Valeur', 'Disponibilité alimentaire en quantité (kg/personne/an)']* main_df['Population_totale']
# Calcul du pourcentage en protéine 
main_df['pourcentage_proteine'] = main_df['disp_alim_kg_pays']/total_weight
main_df.fillna(0, inplace=True)
main_df


# ## Question 5 : 

# In[11]:


# Changer les valeurs "inf" en Nan puis en 0
main_df = main_df.replace(np.inf, 0)

df_5 = main_df.copy()
df_5 = df_5[df_5['pourcentage_proteine'] != 0]
df_5 = df_5.groupby(df_5['Produit','']).mean()
df_5 = df_5.sort_values(by=['pourcentage_proteine'], ascending=False)
df_5.head(20)


# Parmis les 20 aliments les plus riches en protéine on retrouve : 'Graines Colza/Moutarde', 'viande de bovin', 'Arachides Decortiquees', 'Pois', 'Légumineuses Autres'

# In[12]:


df_5 = df_5.sort_values(by=['ratio kcal/kg'], ascending=False)
df_5.head(20)


# Parmis les 20 aliments les plus caloriques on retrouve : 'Arachides Decortiquees', 'Sésame', 'Feve de Cacao', 'Riz (Eq Blanchi)','Millet'

# ## Question 6 :

# In[13]:


df_6 = main_df.copy()
df_6 = df_6[df_6['Type',''] == 'vegetal'].copy()
df_6['Valeur','Disponibilité intérieure'] = df_6['Valeur','Disponibilité intérieure'] * 1000 *1000
df_6['Disponibilité_interieur_kcal'] = df_6['Valeur','Disponibilité intérieure'] * df_6['ratio kcal/kg']
disp_world_kcal = df_6['Disponibilité_interieur_kcal'].sum()
disp_world_kcal


# ## Question 7 :

# In[14]:


# estimation du besoin calorique d'un humain sur 1 an 
human_kcal_year = 2250 * 365

# calcul du nombre d'humains pouvant être nourris par an en termes de kcal
world_human_kcal = disp_world_kcal /human_kcal_year  
world_human_kcal


# In[17]:


# poids moyen d'un être humain dans le monde
moy_weight_human = 62

# besoin moyen d'un être humain en protéine sur 1 an
human_prot_year = (0.8 / 1000) * moy_weight_human * 365 

# Calcul de la disponibilité intérieure végétale en protéine 
df_6['Disponibilité_intérieur_prot'] = df_6['Valeur','Disponibilité intérieure'] * df_6['pourcentage_proteine']

disp_world_prot = df_6['Disponibilité_intérieur_prot'].sum()

human_world_prot = disp_world_prot / human_prot_year
human_world_prot


# In[18]:


# pourcentage par rapport à la population mondiale 
percentage_cal = (world_human_kcal *100) / nb_people
percentage_cal


# environs 214 % de la population mondiale peut être nourrie en termes de kcal

# In[19]:


percentage_prot = (human_world_prot * 100 ) / nb_people
percentage_prot


# environs 230 % de la population peut être nourrie en termes de protéines 

# ## Question 8 :

# Combien d'humains pourraient être nourris si toute la disponibilité alimentaire en produits végétaux, la nourriture végétale destinée aux animaux et les pertes de produits végétaux étaient utilisés pour de la nourriture ? Donnez les résultats en termes de calories, puis de protéines, et exprimez ensuite ces 2 résultats en pourcentage de la population mondiale

# In[20]:


df_8 = df_6.copy()

# additionner les différentes valeurs 'disponibilité alimentaire', 'nourriture destinée aux animaux' et les 'Pertes' pour chaque pays
# créer une colonne pour la disponibilité alimentaire totale  en kg  par pays .

df_8['disp_alim_kg_total'] = df_8['Valeur','Disponibilité alimentaire en quantité (kg/personne/an)'] * df_8['Population_totale']

df_8['poids_alim_anim_pertes_total'] = df_8['disp_alim_kg_total'] + (df_8['Valeur','Aliments pour animaux'] * 1000000) + (df_8['Valeur','Pertes'] * 1000000)
df_8['poids_alim_anim_pertes_total_kcal'] = df_8['poids_alim_anim_pertes_total'] * df_8['ratio kcal/kg']
poids_alim_anim_pertes_total_kcal = df_8['poids_alim_anim_pertes_total_kcal'].sum()
disp_anim_loss_kcal_world = poids_alim_anim_pertes_total_kcal / human_kcal_year
disp_anim_loss_kcal_percentage = (disp_anim_loss_kcal_world * 100/ nb_people)
disp_anim_loss_kcal_percentage


# Le pourcentage représente 159% de la population mondiale qui pourrait être nourrie en termes de calories

# In[22]:


# résultat en termes de proteine 
df_8['poids_alim_anim_pertes_total_prot'] = df_8['poids_alim_anim_pertes_total'] * df_8['pourcentage_proteine']
poids_alim_anim_pertes_total_prot = df_8['poids_alim_anim_pertes_total_prot'].sum()
disp_anim_loss_prot_world = poids_alim_anim_pertes_total_prot / human_prot_year
percentage_prot_world = (disp_anim_loss_prot_world  * 100 / nb_people)
percentage_prot_world


# Le pourcentage représente 161% de la population mondiale qui pourrait être nourrie en termes de protéines

# ## Question 9 :
# 

# Combien d'humains pourraient être nourris avec la disponibilité alimentaire mondiale ? Donnez les résultats en termes de calories, puis de protéines, et exprimez ensuite ces 2 résultats en pourcentage de la population mondiale.

# In[23]:


# calculez la disponibilité alimentaire mondiale kcal 

df_9 = main_df.copy()

disp_alim_kcal_totale = df_9['disp_alim_kcal_pays'].sum()
disp_alim_kcal_world = disp_alim_kcal_totale /  human_kcal_year

disp_alim_kcal_world_percentage  = (disp_alim_kcal_world * 100)/ nb_people

disp_alim_kcal_world_percentage


# cela représente 128 % de la population mondiale qui pourraient être nourri en terme de calories

# In[24]:


# disponibilité alimentaire  mondiale prot
disp_alim_prot_totale = df_9['disp_alim_kg_pays'].sum()
disp_alim_prot_world = disp_alim_prot_totale /  human_prot_year
disp_alim_prot_world_percentage = (disp_alim_prot_world * 100 )/ nb_people
disp_alim_prot_world_percentage 


# cela  représente 163% de la population qui pourrait nourrie en termes de protéines

# ## Question 10 :
# 

# A partir des données téléchargées qui concernent la sous-nutrition, répondez à cette question : Quelle proportion de la population mondiale est considérée comme étant en sous-nutrition ?

# In[25]:


df_10 = sous_alimentation
df_10[df_10['Valeur'] == '<0.1'] = 0
df_10['Valeur'] = pd.to_numeric(df_10['Valeur'])
df_10.fillna(0, inplace = True)


df_10['population'] = df_10['Valeur'] * 1000000
df_10 = df_10[df_10['Année'] == '2012-2014']
df_10 = df_10[df_10['Zone'] != 'Chine']
population_mondial_sous_alim  = df_10['population'].sum()
population_mondial_sous_alim_percentage = (population_mondial_sous_alim * 100)/nb_people
population_mondial_sous_alim_percentage


# Les personnes étant en sous alimentation représente environs 10% de la population mondiale

# # Question 11 :

# En ne prenant en compte que les céréales destinées à l'alimentation (humaine et animale), quelle proportion (en termes de poids) est destinée à l'alimentation animale ?

# In[26]:


code_cerales = cereal['Code Produit'].unique()
df_11 = main_df[main_df['Code Produit',''].isin(code_cerales)]
poids_alim_anim = df_11['Valeur', 'Aliments pour animaux'].sum() *1000000
poids_nourriture = df_11['Valeur', 'Nourriture'].sum() *1000000
poids_totale = poids_alim_anim + poids_nourriture
alim_anim_percentage = (poids_alim_anim * 100)/poids_totale
alim_anim_percentage


# 45% est destiné à l'alimentation animale

# # Question 12 : 
# 

# Sélectionnez parmi les données des bilans alimentaires les informations relatives aux pays dans lesquels la FAO recense des personnes en sous-nutrition

# In[27]:


# pays avec des personnes en sous_nutrition 
df_12 = df_10.copy()
df_12 = df_12[df_12['population'] > 0]

# Sélection des informations relatives à ces pays
df_12_bis = main_df[main_df['Zone',''].isin(df_12['Zone']) ]
df_12_bis


# Repérez les 15 produits les plus exportés par ce groupe de pays.

# In[28]:


df_12_bis['Exportation'] = df_12_bis['Valeur','Exportations - Quantité']
df_12_bis['Importation'] = df_12_bis['Valeur','Importations - Quantité']

df_12_bis['Code produit']
expo = df_12_bis.groupby(by=[df_12_bis['Code produit'], df_12_bis['Produit', '']]).sum().reset_index()
exportation = expo.sort_values(by='Exportation',ascending=False)

exportation_15 = exportation.iloc[:15,:]
exportation_15.reset_index()
exportation_15


# Parmis les données des bilans alimentaires au niveau mondial, sélectionnez les 200 plus grandes importations de ces produits (1 importation = une quantité d'un produit donné importée par un pays donné

# In[29]:



importation = df_12_bis[df_12_bis['Produit',''].isin(exportation_15['Produit',''])]

importation = importation.sort_values(by='Importation',ascending=False)
importation_200 = importation.iloc[:200,:]
importation_200


# Groupez ces importations par produit, afin d'avoir une table contenant 1 ligne pour chacun des 15 produits. Ensuite, calculez pour chaque produit les 2 quantités suivantes : le ratio entre la quantité destinée aux "Autres utilisations" (Other uses) et la disponibilité intérieure. le ratio entre la quantité destinée à la nourriture animale et la quantité destinée à la nourriture (animale + humaine)

# In[30]:


importation_by_product = importation_200.groupby(importation_200['Produit','']).sum()
importation_by_product


#  calculer le ratio entre la quantité destinée aux "Autres utilisations" (Other uses) et la disponibilité intérieure.

# In[31]:


importation_by_product['ratio_other_disp'] = importation_by_product['Valeur','Autres utilisations (non alimentaire)'] / importation_by_product['Valeur','Disponibilité intérieure']
importation_by_product


# le ratio entre la quantité destinée à la nourriture animale et la quantité destinée à la nourriture (animale + humaine)
# 

# In[32]:


importation_by_product['ratio_anim_nourriture'] = importation_by_product['Valeur','Aliments pour animaux'] / (importation_by_product['Valeur','Aliments pour animaux'] + importation_by_product['Valeur','Nourriture'] )
importation_by_product


# Donnez les 3 produits qui ont la plus grande valeur pour chacun des 2 ratios (vous aurez donc 6 produits à citer)

# In[33]:


top_ratio_anim = importation_by_product.sort_values(by='ratio_anim_nourriture', ascending=False)
top_ratio_anim.head(3)


# In[ ]:





# les 3 aliments pour le ratio nourriture destiné aux animaux et la quantité destinée à la nourriture  sont : Maïs , Poissons Pelagique et Soja

# In[34]:


top_ratio_other = importation_by_product.sort_values(by='ratio_other_disp', ascending=False)
top_ratio_other.head(3)


# les 3 aliments pour le ratio entre la quantité destinée aux "Autres utilisations" (Other uses) et la disponibilité intérieure sont : Huile de palme , Manioc et Maïs

# # Question 13 :
# 

# Combien de tonnes de céréales pourraient être libérées si les USA diminuaient leur production de produits animaux de 10% ?

# In[35]:


test = df_11[df_11['Zone',''] == "États-Unis d'Amérique"]
poid_total_anim_usa = test['Valeur', 'Aliments pour animaux'].sum() 
(poid_total_anim_usa * 0.1) * 1000


# cela pourrait libérer 14009600 tonnes de céreales

# # Question 14 :

# En Thaïlande, quelle proportion de manioc est exportée ? Quelle est la proportion de personnes en sous-nutrition?

# In[36]:


thailande_info = df_12_bis[df_12_bis['Zone',''] == 'Thaïlande']
thailande_info_manioc = df_12_bis[(df_12_bis['Zone',''] == 'Thaïlande') &  (df_12_bis['Produit',''] == 'Manioc')]
thailande_info_disp_manioc = thailande_info_manioc['Valeur','Production']
thailande_info_disp_manioc


# In[37]:


export_manioc = (thailande_info_manioc['Exportation'] * 100) / thailande_info_disp_manioc 
export_manioc


# environ 83% de sa production de manioc

# In[38]:


sous_nutrition_thai = df_10[df_10['Zone'] == 'Thaïlande']
sous_nutrition_thai_pop = sous_nutrition_thai['population'] 
thai = sous_nutrition_thai.iloc[0]
thai.population


# In[39]:


thai_pop = population[population['Zone'] == 'Thaïlande']
thai_pop_value = thai_pop['Valeur'] * 1000
thai_pop_value


# In[40]:


sous_nutrition_thai_percentage = (thai.population * 100) / thai_pop_value
sous_nutrition_thai_percentage


# cela représente environ 8% de la population thaïlandaise

# In[ ]:




