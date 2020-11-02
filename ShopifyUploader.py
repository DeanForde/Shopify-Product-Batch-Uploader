import shopify
import pandas as pd
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox


# TODO: make lb scrollable
# TODO: ORDER lb

class GUI:

    def __init__(self, master):
        # Main window
        master.title("Shopify Uploader")
        master.geometry('930x500')

        # Infobox
        self.infobox = Text(master, height=10, width=80, bg="light grey")
        self.infobox.grid(column=1, columnspan=5, row=1, sticky="NE", pady=303)
        self.infobox.tag_configure("ERROR", foreground="red")
        self.infobox.tag_configure("COMPLETE", foreground="green")
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
            master, width=10, text="Upload", command=self.CheckFields)
        self.browseBtn.grid(column=3, row=1, sticky="NW", pady=117)
        self.uploadBtn.grid(column=2, row=1, sticky="N", pady=180)

    def GetAllCollections(self):
        i = 0
        collection_listings = shopify.CollectionListing.find()
        for x in collection_listings:
            self.lb.insert(i, x.handle)  # or x.collection_id
            i += 1

    def LbCallBack(self, event):
        if(self.lb.curselection()):
            value = self.lb.get(self.lb.curselection()[0])
            self.collection.delete(0, END)
            self.collection.insert(0, value)

    def BrowseFiles(self):
        filename = filedialog.askopenfilename(
            initialdir="/", title="Select a File", filetypes=(("all files", "*.*"), ("Text files", "*.txt*")))
        self.csv.insert(0, filename)

    def CheckFields(self):
        if not self.collection.get() or not self.csv.get():
            messagebox.showerror(
                "Error", "Make sure collection name and CSV not empty")
        else:
            self.infobox.delete('1.0', END)
            self.infobox.configure(state="normal")
            self.infobox.insert("end", "Processing, Please Wait..\n")
            self.infobox.update_idletasks()
            collection_id = self.CheckForCollection()
            self.AddProducts(collection_id)

    def CheckForCollection(self):
        try:
            self.infobox.insert("end", "Checking For Existing Collection..\n")
            self.infobox.update_idletasks()
            collection_id = self.GetCollectionId()
            self.infobox.insert("end", "Collection Found\n")
            self.infobox.update_idletasks()
        except:
            self.infobox.insert("end", "No Collection Found For: " +
                                self.collection.get() + ", Creating New Collection. \n")
            self.infobox.update_idletasks()
            collection_id = self.CeateNewCollection()
        return collection_id

    def CeateNewCollection(self):
        try:
            new_collect = shopify.CustomCollection()
            new_collect.title = self.collection.get()
            new_collect.save()
            self.infobox.insert("end", "New Collection Created\n")
            self.infobox.update_idletasks()
            collection_id = self.GetCollectionId()
            return collection_id
        except:
            self.infobox.insert(
                "end", "ERROR: COULD NOT CREATE COLLECTION.\n", 'ERROR')
            self.infobox.update_idletasks()

    def GetCollectionId(self):
        handle = self.collection.get().strip()
        handle = handle.replace(" ", "-")
        collection_id = shopify.CustomCollection.find(handle=handle)[0].id
        return collection_id

    def AddProducts(self, collection_id):
        self.infobox.insert("end", "Adding Products To Collection\n")
        self.infobox.update_idletasks()
        try:
            data = pd.read_csv(self.csv.get())
            for ind in data.index:
                new_product = shopify.Product()
                new_product.title = data['title'][ind]
                new_product.product_type = data['product type'][ind]
                new_product.body_html = data['body'][ind]
                new_product.vendor = data['vendor'][ind]
                new_product.save()
                self.AddToCollection(new_product, collection_id)
                self.infobox.insert(
                    "end", "Added " + new_product.title + " To " + self.collection.get() + "\n")
                self.infobox.update_idletasks()
            self.ClearFields()
        except:
            self.infobox.insert(
                "end", "ERROR: COULD NOT CREATE PRODUCT\n", 'ERROR')
            self.infobox.update_idletasks()

    def AddToCollection(self, new_product, collection_id):
        try:
            add_collection = shopify.Collect(
                {'product_id': new_product.id, 'collection_id': collection_id})
            add_collection.save()
        except:
            self.infobox.insert(
                "end", "ERROR: COULD NOT ADD PRODUCT TO COLLECTION\n", 'ERROR')
            self.infobox.update_idletasks()

    def ClearFields(self):
        self.infobox.insert("end", "Process Complete", 'COMPLETE')
        self.infobox.configure(state="disabled")
        self.collection.delete(0, END)
        self.csv.delete(0, END)


def ConnectToStore():
    API_KEY = ''
    PASSWORD = ''
    SHOP_NAME = ''
    shop_url = "https://%s:%s@%s.myshopify.com/admin" % (
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
