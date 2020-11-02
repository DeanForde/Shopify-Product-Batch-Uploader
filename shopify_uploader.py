import shopify  #pip install shopifyapi
import sys
import os
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

API_KEY = os.environ.get("KEY")
PASSWORD = os.environ.get("PASS")
SHOP_NAME = os.environ.get("SHOP_NAME")

class GUI:

    def __init__(self, master):
        # Main window
        master.title("Shopify Uploader")
        master.geometry('930x500')

        # Infobox
        self.infobox = Text(master, height=10, width=80, bg="light grey")
        self.infobox.grid(column=1, columnspan=5, row=1, sticky="NE", pady=303)
        self.infobox.tag_configure("error", foreground="red")
        self.infobox.tag_configure("complete", foreground="green")
        self.infobox.tag_configure("normal", foreground="black")
        self.infobox.configure(state="disabled")

        # Listbox
        self.lb = Listbox(master, height=29, width=40, bg="white")
        self.lb.grid(row=1, column=0, sticky='N', padx=10)
        self.lb.bind('<<ListboxSelect>>', self.LbCallBack)

        # Textboxes
        self.collection = Entry(master, width=35)
        self.csv = Entry(master, width=35)
        self.collection.grid(column=2, row=1, sticky="NW", pady=80)
        self.csv.grid(column=2, row=1, sticky="NW", pady=120)

        # Labels
        self.lbl1 = Label(master, text="Existing Collections")
        self.lbl2 = Label(master, text="Select From Existing Or Enter New:")
        self.lbl3 = Label(master, text="Select CSV File Or Enter Path:")
        self.lbl1.grid(row=0, column=0, padx=10)
        self.lbl2.grid(column=1, row=1, sticky="NE", pady=80)
        self.lbl3.grid(column=1, row=1, sticky="NE", pady=120)

        # Buttons
        self.browseBtn = Button(
            master, width=10, text="Select", command=self.BrowseFiles)
        self.uploadBtn = Button(
            master, width=10, text="Upload", command=self.Upload)
        self.browseBtn.grid(column=3, row=1, sticky="NW", pady=117)
        self.uploadBtn.grid(column=2, row=1, sticky="N", pady=180)

    def GetAllCollections(self):
        i = 0
        collection_listings = shopify.CollectionListing.find()
        for x in collection_listings:
            self.lb.insert(i, x.handle)
            i += 1

    def LbCallBack(self, event):
        if(self.lb.curselection()):
            self.collection.delete(0, END)
            self.collection.insert(0, self.lb.get(self.lb.curselection()[0]))

    def BrowseFiles(self):
        filename = filedialog.askopenfilename(
            initialdir="/", title="Select a File", filetypes=(("all files", "*.*"), ("Text files", "*.txt*")))
        self.csv.insert(0, filename)

    def Upload(self):
        if not self.collection.get() or not self.csv.get():
            messagebox.showerror(
                "Error", "Make sure collection name and CSV not empty")
        else:
            self.Infobox_Update('Processing, Please Wait..', 'normal')
            collection_id = self.GetCollectionId()
            list_of_products = self.AddProducts()
            self.AddToCollection(list_of_products, collection_id)

    def CeateNewCollection(self):
        try:
            new_collect = shopify.CustomCollection()
            new_collect.title = self.collection.get()
            new_collect.save()
            self.Infobox_Update('New Collection Created', 'complete')
        except:
            raise RuntimeError("Could Not Create A New Collection")

    def GetCollectionId(self):
        try:
            self.Infobox_Update('Checking For Collection In Store', 'normal')
            handle = self.collection.get().strip()
            handle = handle.replace(" ", "-")
            collection_id = shopify.CustomCollection.find(handle=handle)[0].id
            self.Infobox_Update('Collection Found!', 'normal')
            return collection_id
        except:
            self.Infobox_Update(
                'No Collection Found, Creating New Collection', 'normal')
            self.CeateNewCollection()
            collection_id = self.GetCollectionId()

    def ReadFile(self):
        try:
            self.Infobox_Update('Attempting To Read CSV File', 'normal')
            data = pd.read_csv(self.csv.get())
            return data
        except IOError:
            print(IOError)

    def AddProducts(self):
        list_of_products = []
        data = self.ReadFile()
        self.Infobox_Update('Trying To Add Products To Store..', 'normal')
        try:
            for ind in data.index:
                new_product = shopify.Product()
                new_product.title = data['title'][ind]
                new_product.product_type = data['product type'][ind]
                new_product.body_html = data['body'][ind]
                new_product.vendor = data['vendor'][ind]
                new_product.save()
                self.Infobox_Update(
                    'New Product: ' + new_product.title + ' Added Successfully', 'complete')
                list_of_products.append(new_product)
            return list_of_products
        except:
            raise RuntimeError("Could Not Add Product To Store")

    def AddToCollection(self, list_of_products, collection_id):
        try:
            for product in list_of_products:
                add_collection = shopify.Collect(
                    {'product_id': product.id, 'collection_id': collection_id})
                add_collection.save()
                self.Infobox_Update(
                    'All Products Added To Collection Successfully', 'complete')
        except:
            raise RuntimeError("Could Not Add Product To Collection")

    def ClearFields(self):
        self.collection.delete(0, END)
        self.csv.delete(0, END)

    def Infobox_Update(self, message, tag):
        self.infobox.configure(state="normal")
        self.infobox.insert("end", message, tag)
        self.infobox.update_idletasks()
        self.infobox.configure(state="disabled")


def ConnectToStore():
    shop_url = "https://%s:%s@:%s.myshopify.com/admin" % (
        API_KEY, PASSWORD, SHOP_NAME)
    shopify.ShopifyResource.set_site(shop_url)


def main():
    ConnectToStore()
    root = Tk()
    b = GUI(root)
    b.GetAllCollections()
    root.mainloop()


if __name__ == "__main__":
    main()
